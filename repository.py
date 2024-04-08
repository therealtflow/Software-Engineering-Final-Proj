#import statements
import firebase_admin
from firebase_admin import credentials, firestore, auth

#declares credentials to access firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

#sets up firebase client
db = firestore.client()


#############################################################################################################################################################################################################################################
#ACCOUNT RELATED FUNCTIONS
##########################

#sets all the data in repository, returning the id for the document that contains all of the information
def create_account(Username, Email, AboutMe, Password):
    user = auth.create_user(email = Email, password = Password)
    new_account_ref = db.collection('Users').document(user.uid)
    new_account_data = {'Username': Username, 'Email': Email, 'AboutMe': AboutMe, 'Password': Password}
    new_account_ref.set(new_account_data)
    new_account_id = new_account_ref.id
    return new_account_id

#returns the data from a user account from recieving the acct_id
def get_account(acct_id):
    acct_ref = db.collection('Users').document(acct_id)
    doc = acct_ref.get()
    if doc:
        acct_data = doc.to_dict()
        return acct_data
    else:
        return None

#logs out the active user
def logout_user(uid):
    auth.revoke_refresh_tokens(uid)
    return None

#deletes the current user
def delete_user(uid):
    auth.revoke_refresh_tokens(uid)
    db.collection('Users').document(uid).delete()
    auth.delete_user(uid)
    return None

#verify's that login is valid and sets the session token
def verify(email, password):
    try:
        user = auth.get_user_by_email(email)
        print (user)
        print (user.email)
        print (user.uid)
        ref = db.collection('Users').document(user.uid).get().to_dict()
        print (ref)
        if user and ref['Password'] == password:
            print("Login Successful")
            sessionToken = auth.create_custom_token(user.uid)
            print(sessionToken)
            return user.uid
        else: 
            print("Invalid Email or Password")
    except Exception as e:
        print("Authentication Failed: ", str(e))
        return None


#############################################################################################################################################################################################################################################
#POST RELATED FUNCTIONS
#######################

#gets all posts in database
def get_all_posts():
    all_posts = []
    post_ref = db.collection('Post')
    docs = post_ref.get()
    for doc in docs:
        post_data = doc.to_dict()
        all_posts.append(post_data)
    return all_posts

#gets a single post with post_id
def get_one_post(post_id):
    single_post = db.collection('Post').document(post_id)
    doc = single_post.get()
    if doc:
        post_data = doc.to_dict()
        return post_data
    else:
        return None

#uploads post to database
def create_post(Name, Link, Description, CreatedBy, Code, tag ):
    new_post_ref = db.collection('Post').document()
    new_post_data = {'Name': Name, 'Link': Link, 'Description': Description, 'CreatedBy': CreatedBy, 'Code': Code, 'post_id' : new_post_ref.id, 'tag' : tag, 'comments': []}
    new_post_ref.set(new_post_data)
    new_post_id = new_post_ref.id
    return new_post_id

#gets all posts from a selected user
def get_user_posts(username):
    users_posts = []
    posts_docs = db.collection('Post').where('CreatedBy', '==', username).get()
    for doc in posts_docs:
        post_data = doc.to_dict()
        users_posts.append(post_data)
    return users_posts

#deletes post from database
def delete_post(post_id):
    post_doc = db.collection('Post').document(post_id)
    print(post_doc)
    post_doc.delete()
    return None


#############################################################################################################################################################################################################################################
#COMMENT RELATED FUNCTIONS
##########################

#adds comment to the database
#WHAT ARGUMENTS TO GIVE THE FUNCTION
#post_id - the post that you will be adding comment to
#username - the user that is currently logged in
#comment - the text of the comment that is being added 
def add_comment(post_id, username, comment):
    try:
        post_ref = db.collection('Post').document(post_id)
        post_ref.update({
            'comments': firestore.ArrayUnion([username + ": " + comment])
        })
        print('success')
    except Exception as e:
        print("Failed to add comment:", str(e))

#gets all commments for a post
#WHAT TO USE WHEN GETTING COMMENTS
#formatted_comments[i].username for username
#formatted_comments[i].text for text
def get_comments(post_id):
    post_doc = db.collection('Post').document(post_id).get()

    if post_doc.exists:
        comments = post_doc.to_dict()['comments']

        formatted_comments = []
        for comment in comments: 
            #username = comment.split(" - ")[1]
            #text = comment.split(" - ")[0]
            #formatted_comments.append({
            #    'username': username,
            #    'text': text
            #})
            formatted_comments.append(comment)
            print(formatted_comments)
            return formatted_comments
    else:
        return []
