from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import SECRET_KEY
from db import get_connection
import os
import uuid
import pymysql
pymysql.install_as_MySQLdb()
from dotenv import load_dotenv
load_dotenv()



from datetime import datetime
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url


# Configuration       
cloudinary.config( 
    cloud_name = "dud9elfag", 
    api_key = "566776174283142", 
    api_secret = "yc2tiq-RNmTW2ul0TiQLOlTbNHA", # Click 'View API Keys' above to copy your API secret
    secure=True
)

# Upload an image


def upload_file(file):
    try:
        # first assign folder and resource-type based on filetype:
        result = cloudinary.uploader.upload(
            file,
            resource_type='image'
        )
        return {"success": True, "secure_url": result['secure_url'], "public_id": result['public_id']}
    except Exception as e:
        return {"success": False, "error": str(e)}


app = Flask(__name__)
app.secret_key = SECRET_KEY

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/contact')
def contact():
    return render_template('contactus.html')


@app.route('/login-register', methods=['GET'])
def login_register():
    return render_template('login_register.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    hashed_pw = generate_password_hash(password)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
    user_exists = cursor.fetchone()

    if user_exists:
        flash("Username or Email already exists!", "error")
        return redirect(url_for('login_register'))

    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                   (username, email, hashed_pw))
    conn.commit()
    user_id = cursor.lastrowid

    session['user_id'] = user_id
    session['username'] = username

    cursor.close()
    conn.close()

    flash("Account created successfully!", "success")
    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash("Login successful!", "success")
        return redirect(url_for('explore'))
    else:
        flash("Invalid username or password", "error")
        return redirect(url_for('login_register'))


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('login_register'))


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash("Please login to continue", "error")
            return redirect(url_for('login_register'))

        looking_for = request.form['looking_for']
        age_min = request.form['age_min']
        age_max = request.form['age_max']
        mother_tongue = request.form['mother_tongue']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users_preferences (user_id, looking_for, age_min, age_max, mother_tongue)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, looking_for, age_min, age_max, mother_tongue))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('profile'))

    return render_template('index.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash("Please login to continue", "error")
            return redirect(url_for('login_register'))

        profile_for = request.form['profile_for']
        gender = request.form['gender']
        first_name = request.form['first_name']
        middle_name = request.form.get('middle_name', '')
        last_name = request.form['last_name']
        father_name = request.form['father_name']
        mother_name = request.form['mother_name']
        dob = request.form['dob']
        age = request.form['age']
        religion = request.form['religion']
        gotra = request.form['gotra']
        mother_tongue = request.form['mother_tongue']
        height = request.form['height']
        email = request.form['email']
        phone = request.form['phone']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO profiles_basic_info (
                user_id, profile_for, gender, first_name, middle_name, last_name,
                father_name, mother_name, dob, age, religion, gotra,
                mother_tongue, height, email, phone
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, profile_for, gender, first_name, middle_name, last_name,
            father_name, mother_name, dob, age, religion, gotra,
            mother_tongue, height, email, phone
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('profile2'))  # next page (to be added later)

    return render_template('profile.html')

@app.route('/profile2', methods=['GET', 'POST'])
def profile2():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash("Please login to continue", "error")
            return redirect(url_for('login_register'))

        # Fetch temporary address fields
        temp_address = request.form.get('temp_address', '')
        temp_city = request.form.get('temp_city', '')
        temp_district = request.form.get('temp_district', '')
        temp_state = request.form.get('temp_state', '')
        temp_pincode = request.form.get('temp_pincode', '')

        # Check if permanent address is same as temporary
        same_as_temp = request.form.get('same_as_temp')
        if same_as_temp:
            perm_address = temp_address
            perm_city = temp_city
            perm_district = temp_district
            perm_state = temp_state
            perm_pincode = temp_pincode
        else:
            # Fetch permanent address fields safely
            perm_address = request.form.get('perm_address', '')
            perm_city = request.form.get('perm_city', '')
            perm_district = request.form.get('perm_district', '')
            perm_state = request.form.get('perm_state', '')
            perm_pincode = request.form.get('perm_pincode', '')

        # Other fields
        lives_with_family = request.form.get('lives_with_family', '')
        marital_status = request.form.get('marital_status', '')
        diet = ','.join(request.form.getlist('diet'))

        # Insert into DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO addresses (
                user_id, temp_address, temp_city, temp_district, temp_state, temp_pincode,
                perm_address, perm_city, perm_district, perm_state, perm_pincode,
                lives_with_family, marital_status, diet
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            temp_address, temp_city, temp_district, temp_state, temp_pincode,
            perm_address, perm_city, perm_district, perm_state, perm_pincode,
            lives_with_family, marital_status, diet
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('profile3'))

    return render_template('profile2.html')


@app.route('/profile3', methods=['GET', 'POST'])
def profile3():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash("Please login to continue", "error")
            return redirect(url_for('login_register'))

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO education_career (
                user_id, qualification, specialization, working_status,
                works_with, job_title, income, instagram, facebook, linkedin
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            request.form['qualification'],
            request.form.get('specialization'),
            request.form['working_status'],
            request.form.get('works_with'),
            request.form.get('job_title'),
            request.form['income'],
            request.form.get('instagram'),
            request.form.get('facebook'),
            request.form.get('linkedin')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('profile4'))

    return render_template('profile3.html')


@app.route('/profile4', methods=['GET', 'POST'])
def profile4():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash("Please login to continue", "error")
            return redirect(url_for('login_register'))

        identity_type = request.form['identity_type']
        identity_number = request.form['identity_number']
        profile_picture = request.files['profile_picture']

        image_url = None
        if profile_picture and profile_picture.filename:
            try:
                upload_result = cloudinary.uploader.upload(profile_picture, resource_type='image')
                print("Upload successful:", upload_result)
                image_url = upload_result.get('secure_url')
            except Exception as e:
                print("Error during upload:", e)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO identity_verification (user_id, identity_type, identity_number, profile_picture)
            VALUES (%s, %s, %s, %s)
        """, (
            user_id, identity_type, identity_number,
            image_url
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('success'))

    return render_template('profile4.html')

@app.route('/success')
def success():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please login to continue", "error")
        return redirect(url_for('login_register'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    profile_data = {}

    try:
        cursor.execute("SELECT * FROM users_preferences WHERE user_id = %s", (user_id,))
        preferences = cursor.fetchall()
        profile_data['preferences'] = preferences[0] if preferences else None

        cursor.execute("SELECT * FROM profiles_basic_info WHERE user_id = %s", (user_id,))
        basic_info = cursor.fetchall()
        profile_data['basic_info'] = basic_info[0] if basic_info else None

        cursor.execute("SELECT * FROM addresses WHERE user_id = %s", (user_id,))
        address = cursor.fetchall()
        profile_data['address'] = address[0] if address else None

        cursor.execute("SELECT * FROM education_career WHERE user_id = %s", (user_id,))
        career = cursor.fetchall()
        profile_data['career'] = career[0] if career else None

        cursor.execute("SELECT * FROM identity_verification WHERE user_id = %s", (user_id,))
        identity = cursor.fetchall()
        profile_data['identity'] = identity[0] if identity else None

    except Exception as e:
        print("Error fetching profile data:", e)
        flash("There was a problem loading your profile.", "error")
        return redirect(url_for('success'))

    finally:
        cursor.close()
        conn.close()

    return render_template('success.html', profile_data=profile_data)

@app.route('/profile_success')
def profile_success():
    return render_template('profile_success.html')

@app.route('/explore', methods=['GET'])
def explore():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please login to continue", "error")
        return redirect(url_for('login_register'))

    # Get filter parameters from request
    gender = request.args.get('gender')
    mother_tongue = request.args.get('mother_tongue')
    city = request.args.get('city')
    gotra = request.args.get('gotra')

    # Base query
    query = """
        SELECT 
            p.id, CONCAT(p.first_name, ' ', p.last_name) AS name, p.age,
            p.mother_tongue, p.gotra, a.temp_city AS city,
            i.profile_picture, p.gender
        FROM profiles_basic_info p
        LEFT JOIN addresses a ON p.user_id = a.user_id
        LEFT JOIN identity_verification i ON p.user_id = i.user_id
        WHERE p.user_id != %s
    """
    params = [user_id]

    # Build filter conditions
    filter_conditions = []
    
    if gender and gender != "Any":
        filter_conditions.append("p.gender = %s")
        params.append(gender)
    
    if mother_tongue and mother_tongue != "Any":
        filter_conditions.append("p.mother_tongue = %s")
        params.append(mother_tongue)
    
    if city and city != "Any":
        filter_conditions.append("a.temp_city = %s")
        params.append(city)
    
    if gotra and gotra != "Any":
        filter_conditions.append("p.gotra = %s")
        params.append(gotra)

    # Add filter conditions to query if any exist
    if filter_conditions:
        query += " AND " + " AND ".join(filter_conditions)

    # Get user's preferences
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Execute the query
    cursor.execute(query, tuple(params))
    profiles = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('explore.html', 
                         profiles=profiles,
                         current_filters={
                             'gender': gender,
                             'mother_tongue': mother_tongue,
                             'city': city,
                             'gotra': gotra
                         })

@app.route('/profile/<int:profile_id>')
def profile_detail(profile_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT 
            p.first_name AS name_first,
            p.last_name AS name_last,
            p.gender,
            p.dob,
            p.religion,
            p.mother_tongue,
            p.gotra,
            p.age,
            a.temp_address,
            a.temp_city,
            a.temp_state,
            a.perm_address,
            a.lives_with_family,
            a.marital_status,
            a.diet,
            e.qualification,
            e.specialization,
            e.working_status,
            e.works_with,
            e.job_title,
            e.income,
            e.instagram,
            e.facebook,
            e.linkedin,
            p.phone,
            up.looking_for,
            up.age_min,
            up.age_max
        FROM profiles_basic_info p
        LEFT JOIN addresses a ON p.user_id = a.user_id
        LEFT JOIN education_career e ON p.user_id = e.user_id
        LEFT JOIN users_preferences up ON p.user_id = up.user_id
        WHERE p.id = %s
    """, (profile_id,))

    profile = cursor.fetchone()

    cursor.close()
    conn.close()

    if not profile:
        flash("Profile not found", "error")
        return redirect(url_for('explore'))

    return render_template('profile_detail.html', profile=profile)
@app.route('/myprofile')
def myprofile():
    if 'user_id' not in session:
        flash("Please log in to view your profile.", "error")
        return redirect(url_for('login_register'))

    user_id = session['user_id']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    try:
        cursor.execute("""
            SELECT 
                -- User Info
                u.email,

                -- Basic Info
                p.first_name AS name_first,
                p.last_name AS name_last,
                p.age, p.gender, p.dob, p.mother_tongue, p.gotra, p.phone,

                -- Address Info
                a.temp_address, a.temp_city, a.temp_district, a.temp_state, a.temp_pincode,
                a.perm_address, a.perm_city, a.perm_district, a.perm_state, a.perm_pincode,
                a.lives_with_family, a.marital_status, a.diet,

                -- Identity Info
                iv.profile_picture, iv.identity_type,

                -- Education & Career
                ec.qualification, ec.specialization, ec.working_status, ec.works_with,
                ec.job_title, ec.income,
                ec.instagram, ec.facebook, ec.linkedin,

                -- Preferences
                up.looking_for, up.age_min, up.age_max, up.mother_tongue AS pref_mother_tongue

            FROM users u
            LEFT JOIN profiles_basic_info p ON u.id = p.user_id
            LEFT JOIN addresses a ON u.id = a.user_id
            LEFT JOIN identity_verification iv ON u.id = iv.user_id
            LEFT JOIN education_career ec ON u.id = ec.user_id
            LEFT JOIN users_preferences up ON u.id = up.user_id
            WHERE u.id = %s
        """, (user_id,))
        profile = cursor.fetchone()

    finally:
        cursor.close()
        conn.close()

    if not profile:
        flash("Profile not found.", "error")
        return redirect(url_for('index'))

    return render_template('myprofile.html', profile=profile)







if __name__ == '__main__':
    app.run(debug=True)
