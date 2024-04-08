#adding import statements
from flask import Flask, jsonify, render_template, url_for, request, redirect, abort, session
from repository import *

#declares app
app = Flask(__name__)

#sets secret key
app.secret_key = "LOOP"


#############################################################################################################################################################################################################################################
#BASE PAGES & RUNNING APP
#########################

#runs app
if __name__ == "__main__":
    app.run()

#renders template for home
@app.route('/')
def index():
    return render_template('home.html')

#renders template for home
@app.route('/Home')
def home():
    return render_template('home.html')


#############################################################################################################################################################################################################################################
#USER RELATED FUNCTIONS
#######################

#logs in user and sets sessionToken id
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # Extract login credentials from request
        email = request.form.get('email')
        password = request.form.get('password')
        print(email)
        print(password)
        # Sign in the user
        sessionToken_id = verify(email, password)
        print(sessionToken_id)
        user_dict = db.collection('Users').document(sessionToken_id).get().to_dict()
        print(user_dict)
        print('--------')
        if user_dict != None:
            session['user'] = {
                'st_id': sessionToken_id,
                'Username': user_dict['Username'],
                'user_dict': user_dict
            }
        else:
            return redirect('/login')
        return redirect('/feed')
    return render_template('login.html')

#logs out user
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    logout_user(session['user']['st_id'])
    del session['user']
    return redirect(url_for('login'))

#Creates account, sending to repository.py
@app.route('/create_profile', methods=['GET', 'POST'])
def create_acct():
    if request.method == 'POST':
        Username = request.form.get('new_username')
        Email = request.form.get('new_email')
        AboutMe = request.form.get('new_aboutme')
        Password = request.form.get('new_password')
        new_account_id = create_account(Username = Username, Email = Email, AboutMe = AboutMe, Password = Password)
        print('Registration successful. Please login to continue.')
        return redirect('/login')
    return render_template('Profile_Create.html')

#deletes account, calling function from repository.py
@app.route('/delete_acct')
def del_acct():
    delete_user(session['user']['st_id'])
    del session['user']
    return redirect(url_for('login'))

#renders template for home account page
@app.route('/profile')
def home_acct():
    user_info = session.get('user', None)

    if user_info is None:
        return redirect(url_for('login'))
    
    print(user_info)
    posts = get_user_posts(user_info['Username'])

    return render_template('Account_page.html', account = user_info['user_dict'], posts = posts)


#############################################################################################################################################################################################################################################
#FEED RELATED METHODS
#####################

#adds element to feed
def add_element_to_feed(element):

        open("Feed_page.html", "r+")
        contents = file.read()
        start_index = contents.index("</template>") + 6  # find the index of "<body>" and add 6 to get after the tag
        new_contents = contents[:start_index] + "\n" + element + "\n" + contents[start_index:]  # insert new element
        file.seek(0)  # go back to the beginning of the file
        file.write(new_contents)  # overwrite with the new contents
        file.close()
        print ('Feed_page updated. File closed')

#renders template for the feed page
@app.route('/feed')
def feed():
    user_info = session.get('user', None)

    if user_info is None:
        return redirect(url_for('login'))
    try:
        print(user_info)
        all_posts = get_all_posts()
        print(all_posts)
        return render_template('Feed_page.html', posts=all_posts, username = user_info['Username'])
    except Exception as e:
        abort(500, f"Internal Server Error: {str(e)}")

#############################################################################################################################################################################################################################################
#POST RELATED FUNCTIONS
#######################

#uploads post and calls function from repository.py
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    print(request.method)
    user_info = session.get('user', None)
    if user_info is None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        Name = request.form.get("new_name")
        Link = request.form.get("new_link")
        Description = request.form.get("new_description")
        CreatedBy = user_info['Username']
        Code = request.form.get("new_code")
        tag = request.form.get("new_tag")
        print(Name)
        print(Link)
        print(Description)
        print(CreatedBy)
        print(tag)
    
        if not Name or not Link or not Description or not CreatedBy or not Code or not tag:
            abort(400, "Missing required information. Please fill out all fields.")

        new_post_id = create_post(Name = Name, Link = Link, Description = Description, CreatedBy = CreatedBy, Code = Code, tag = tag)
        if new_post_id:
            add_comment(new_post_id, 'loop-official', 'Welcome to the LOOP Comment Section! Please be respectful and on topic.')
            return redirect('/feed')
        else:
            return abort(500, "Failed to Create Post")
    return render_template('upload.html')

#second upload function
@app.post('/upload')
def new_post():
    user_info = session.get('user', None)
    if user_info is None:
        return redirect(url_for('login'))
    Name = request.form.get("new_name")
    Link = request.form.get("new_link")
    Description = request.form.get("new_description")
    CreatedBy = user_info['Username']
    Code = request.form.get("new_code")
    print('Upload successful.')
    
    if not Name or not Link or not Description or not CreatedBy or not Code:
        abort(400, "Missing required information. Please fill out all fields.")

    new_post_id = create_post(Name = Name, Link = Link, Description = Description, CreatedBy = CreatedBy, Code = Code)
    return redirect('/feed')

#gets single post calling repository,py function
@app.route('/Post/<post_id>')
def get_post(post_id):
    user_info = session.get('user', None)

    single_post = get_one_post(post_id)
    if single_post:
       if single_post['CreatedBy'] == user_info['Username']:
           CreatedBy = True
       else:
           CreatedBy = False
       comments = get_comments(post_id)
       print(comments)
               
       return render_template('Post_Page.html', post_id = post_id, post = single_post, username = user_info, CreatedBy = CreatedBy, comments = comments)
    return render_template('Post_Page.html')

#deletes post, calling repository.py function
@app.route('/Post/delete/<post_id>')
def del_post(post_id):
    # post_id = request.form.get('post_id')
    print(post_id)
    delete_post(post_id)
    return redirect('/profile')


#############################################################################################################################################################################################################################################
#COMMENT RELATED FUNCTIONS
##########################

#adds comment 
#TODO
#FRONT END - when you are adding comment use /comment
@app.route('/Post/<post_id>/comment', methods=['POST'])
def add_comment_route(post_id):
    user_info = session.get('user', None)
    #post_id = request.args.get('post_id')
    comment = request.form.get('comment')
    username = user_info['Username']
    print(post_id)
    print(comment)
    print(username)

    add_comment(post_id, username, comment)
    return redirect(f'/Post/{post_id}')
