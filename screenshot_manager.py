# Importing libraries that are needed
import os # os = operating system
import datetime # The datetime module supplies classes for manipulating dates and times .
from flask import Flask, render_template, send_file, request, url_for, redirect # flask is used to build website

# doc_path= "/Users/chrisjames/Documents" #path of where I keep all my screenshot

def get_screenshot(doc_path, old_pic_threshold):
    screenshots = [] # a list to store screenshots
    for dirpath, dirnames,filenames in os.walk(doc_path):
        for file in filenames:
            full_path = os.path.join(dirpath, file) 
            if file.startswith("Screenshot") and file.endswith(".png"): 
                # creating timestamp
                created_timestamp = os.path.getmtime(full_path) # grabs the file modification time (created time was not working for me b/c of Mac?)
                created_date = datetime.datetime.fromtimestamp(created_timestamp) # Return the local date
                days_diff = (datetime.datetime.now() - created_date).days # subtracting current date today subtracted the created day of the file
                # check if it's older than 200 days (can customize this to whatever liking but I chose 200 days since that's how long a semester is)
                is_old = days_diff > old_pic_threshold
                screenshots.append({
                    "path": full_path,
                    "filename": file,
                    "days_old": days_diff,
                    "is_old": is_old
                })
    return screenshots

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"]) # Get receives data and post sends data. 
def home():
    if request.method == "POST": #submitting form used to ask user for their files.
        doc_path = request.form.get("doc_path")
        try:
            old_pic = int(request.form.get("old_pic"))
        except (TypeError, ValueError):
            old_pic = 200 # If request does not work, default to 200 days old 
        return redirect(url_for("home", doc_path=doc_path, old_pic=old_pic, index=0)) #redirecting back to home page, with the first pic. 

    doc_path = request.args.get("doc_path")
    old_pic = int(request.args.get("old_pic", 200))

    # If doc_path is still None, render beginning page (asking user for doc_path and what's considered an old pic). 
    if not doc_path:
        return render_template("input.html")
    
    try:
        old_pic = int(old_pic)
    except ValueError:
        old_pic = 200
    
    index = int(request.args.get("index", default=0))
    screenshots = get_screenshot(doc_path, old_pic)
    total = len(screenshots)
    old_screenshots = []  # a list to store old screenshots

    for screenshot in screenshots:
        if screenshot["is_old"]:  # check if screenshot is marked as old
            old_screenshots.append(screenshot)  # add to the list if it is

    old = len(old_screenshots)

    # testing screenshot for review
    current = screenshots[index] if index < total else None 

    return render_template("screenshot.html", screenshot=current, total=total, old=old, index=index, doc_path=doc_path, old_pic=old_pic)


# Route for "Skipping screenshot"
@app.route('/skip',methods=["POST"]) # needs post method to interact
def skip():
    index_raw = request.form.get("index")
    try:
        index = int(index_raw)
    except (TypeError, ValueError):
        index = 0  # fallback to default
    doc_path = request.form.get("doc_path")
    try:
        old_pic = int(request.form.get("old_pic"))
    except (TypeError, ValueError):
        old_pic = 200 
    return redirect(url_for("home", index=index + 1, doc_path = doc_path, old_pic = old_pic)) # if click skip should redirect back to home page and new screenshot

# Route for "Deleting screenshot"
@app.route('/delete',methods=["POST"]) # needs post method to interact
def delete():
    filepath = request.form.get("filepath")
    index = int(request.form.get("index", 0))
    doc_path = request.form.get("doc_path")
    old_pic = int(request.form.get("old_pic"))
    if filepath and os.path.exists(filepath):
        os.remove(filepath)
        # say it delted image and go back to home page 
    return redirect(url_for("home", index=index + 1, doc_path = doc_path, old_pic = old_pic))

# Route for image
@app.route("/image")
def image():
    filepath = request.args.get("filepath")
    if filepath and os.path.exists(filepath):
        return send_file(filepath)
    return "Image not found", 404

app.run(debug=True)