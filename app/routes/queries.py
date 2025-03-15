from flask import Blueprint, render_template, request
from app.database import Database

queries_bp = Blueprint("query", __name__)

# helper function to execute a query and return the result
def execute_query(query, params):
    db = Database()
    return db.execute(query, params)

# 1. List all tables in the database
@queries_bp.route('/list_tables', methods=['GET'])
def list_tables():
    query = "SHOW TABLES"
    result = execute_query(query, [])
    return render_template('list_tables.html', tables=result)

# 2. Search for a motion picture by its name
@queries_bp.route('/search_movie', methods=['GET', 'POST'])
def search_movie():
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        query = """
            SELECT name, rating, production, budget
            FROM MotionPicture
            WHERE name LIKE %s;
        """
        result = execute_query(query, [f'%{movie_name}%'])
        return render_template('search_movie.html', movies=result)
    return render_template('search_movie.html')

# 3. Find the movies that have been liked by a specific user’s email
@queries_bp.route('/liked_movies', methods=['GET', 'POST'])
def liked_movies():
    if request.method == 'POST':
        user_email = request.form['user_email']
        query = """
            SELECT mp.name, mp.rating, mp.production, mp.budget
            FROM MotionPicture mp
            JOIN Likes l ON mp.mpid = l.mpid
            JOIN User u ON l.uemail = u.email
            WHERE u.email = %s;
        """
        result = execute_query(query, [user_email])
        return render_template('liked_movies.html', movies=result)
    return render_template('liked_movies.html')

# 4. Search motion pictures by their shooting location country
@queries_bp.route('/search_location', methods=['GET', 'POST'])
def search_location():
    if request.method == 'POST':
        country = request.form['country']
        query = """
            SELECT DISTINCT mp.name
            FROM MotionPicture mp
            JOIN Location l ON mp.mpid = l.mpid
            WHERE l.country = %s;
        """
        result = execute_query(query, [country])
        return render_template('search_location.html', movies=result)
    return render_template('search_location.html')

# 5. List all directors who have directed TV series shot in a specific zip code
@queries_bp.route('/directors_by_zip', methods=['GET', 'POST'])
def directors_by_zip():
    if request.method == 'POST':
        zip_code = request.form['zip_code']
        query = """
            SELECT DISTINCT p.name, s.mpid
            FROM People p
            JOIN Role r ON p.id = r.pid
            JOIN Series s ON r.mpid = s.mpid
            JOIN Location l ON s.mpid = l.mpid
            WHERE l.zip = %s;
        """
        result = execute_query(query, [zip_code])
        return render_template('directors_by_zip.html', directors=result)
    return render_template('directors_by_zip.html')

# 6. Find people who have received more than “k” awards for a single motion picture in the same year
@queries_bp.route('/award_winners', methods=['GET', 'POST'])
def award_winners():
    if request.method == 'POST':
        k = int(request.form['k'])
        query = """
            SELECT p.name, mp.name, a.award_year, COUNT(*) AS award_count
            FROM People p
            JOIN Award a ON p.id = a.pid
            JOIN MotionPicture mp ON a.mpid = mp.mpid
            GROUP BY p.id, mp.mpid, a.award_year
            HAVING award_count > %s;
        """
        result = execute_query(query, [k])
        return render_template('award_winners.html', winners=result)
    return render_template('award_winners.html')

# 7. Find the youngest and oldest actors to win at least one award
@queries_bp.route('/youngest_oldest_actors', methods=['GET'])
def youngest_oldest_actors():
    query = """
        SELECT p.name, (YEAR(a.award_year) - YEAR(p.dob)) AS age
        FROM People p
        JOIN Award a ON p.id = a.pid
        WHERE p.role = 'actor'
        ORDER BY age DESC;
    """
    result = execute_query(query, [])
    return render_template('youngest_oldest_actors.html', actors=result)

# 8. Find the American Producers who had a box office collection of more than or equal to “X” (parameterized) with a budget less than or equal to “Y” (parameterized). List the producer name, movie name, box office collection, and budget.

# 9. List the people who have played multiple roles in a motion picture where the rating is more than “X” (parameterized). List the person’s and motion picture names, and count the number of roles for that particular picture.

# 10. Find the top 2 rates thriller movies (genre is thriller) that were shot exclusively in Boston. This means that the movie cannot have any other shooting location. List the movie names and their ratings.

# 11. Find all the movies with more than “X” (parameterized) likes by users of age less than “Y” (parameterized). List the movie names and the number of likes by those age-group users.

# 12. Find the actors who have played a role in both “Marvel” and “Warner Bros” productions. List the actor names and the corresponding motion picture names.

# 13. Find the motion pictures with a higher rating than the average rating of all comedy (genre) motion pictures. Show the names and ratings in descending order of ratings.

# 14. Find the top 5 movies with the most people playing a role in that movie. Show the movie name, people count, and role count for the movies.

# 15. Find actors who share the same birthday. List the actors’ names (actors 1 and 2) and their common birthday.