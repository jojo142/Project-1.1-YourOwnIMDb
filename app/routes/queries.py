from flask import Blueprint, render_template, request
from app.database import Database

queries_bp = Blueprint("query", __name__)

# helper function to execute a query and return the result
def execute_query(query, params=None):
    with Database() as db:
        result = db.execute(query, params)
    return result

# 1. List all tables in the database
@queries_bp.route('/list_tables', methods=['GET'])
def list_tables():
    query = "SHOW TABLES;"
    tables = execute_query(query)
    return render_template('list_tables.html', tables=tables)

# 2. Search for a motion picture by its name
@queries_bp.route('/search_movie', methods=['POST'])
def search_movie():
    movie_name = request.form['movie_name']
    query = """
        SELECT name, rating, production, budget
        FROM MotionPicture
        WHERE name LIKE %s;
    """
    movies = execute_query(query, [f'%{movie_name}%'])
    return render_template("search_results.html", movies=movies)

# 3. Find the movies that have been liked by a specific user’s email
@queries_bp.route('/search_liked_movies', methods=['POST'])
def liked_movies():
    user_email = request.form['user_email']
    query = """
        SELECT mp.name, mp.rating, mp.production, mp.budget
        FROM MotionPicture mp
        JOIN Likes l ON mp.id = l.mpid
        JOIN User u ON l.uemail = u.email
        WHERE u.email = %s;
    """
    movies = execute_query(query, [user_email])
    return render_template('search_results.html', movies=movies)

# 4. Search motion pictures by their shooting location country
@queries_bp.route("/search_by_country", methods=['POST'])
def search_location():
    country = request.form['country']
    query = """
        SELECT DISTINCT mp.name
        FROM MotionPicture mp
        JOIN Location l ON mp.id = l.mpid
        WHERE l.country = %s;
    """
    movies = execute_query(query, [country])
    return render_template("search_results_by_country.html", movies=movies)

# 5. List all directors who have directed TV series shot in a specific zip code
@queries_bp.route("/search_directors_by_zip", methods=['POST'])
def directors_by_zip():
    zip_code = request.form['zip_code']
    query = """
    SELECT p.name, mp.name
    FROM (SELECT r.pid, l.mpid
    FROM Location l JOIN Role r
    ON l.mpid = r.mpid
    WHERE l.zip= %s AND r.role_name = "Director") AS Ids
    JOIN People p ON Ids.pid = p.id 
    JOIN MotionPicture mp ON Ids.mpid = mp.id
    WHERE mp.id IN (SELECT s.mpid
    FROM Series s);
    """
    results = execute_query(query, [zip_code])
    return render_template("search_directors_results.html", results=results)

# 6. Find people who have received more than “k” awards for a single motion picture in the same year
@queries_bp.route("/search_awards", methods=['POST'])
def award_winners():
    k = int(request.form['k'])
    query = """
        SELECT p.name, mp.name, a.award_year, COUNT(*) AS award_count
        FROM People p
        JOIN Award a ON p.id = a.pid
        JOIN MotionPicture mp ON a.mpid = mp.id
        GROUP BY p.id, mp.id, a.award_year
        HAVING award_count > %s;
    """
    results = execute_query(query, [k])
    return render_template("search_awards_results.html", results=results)

# 7. Find the youngest and oldest actors to win at least one award
'''Needs to be revised'''
@queries_bp.route("/find_youngest_oldest_actors", methods=['GET'])
def youngest_oldest_actors():
    query = """
        SELECT p.name, (a.award_year - YEAR(p.dob)) AS age, a.award_name
        FROM People p
        JOIN Award a ON p.id = a.pid
        JOIN Role r ON p.id = r.pid
        WHERE r.role_name = 'Actor';
    """
        
    actors = execute_query(query)
    
    # Filter out actors with null ages (if any)
    actors = [actor for actor in actors if actor[1] is not None]
    if actors:
        min_age = min(actors, key=lambda x: x[1])[1]
        max_age = max(actors, key=lambda x: x[1])[1]
        youngest_actors = [actor for actor in actors if actor[1] == min_age]
        oldest_actors = [actor for actor in actors if actor[1] == max_age]
        return render_template(
            "actors_by_age.html",
            youngest_actors=youngest_actors,
            oldest_actors=oldest_actors,
        )
    else:
        return render_template(
            "actors_by_age.html", youngest_actors=[], oldest_actors=[]
        )
# 8. Find the American Producers who had a box office collection of more than or equal to “X” (parameterized) 
# with a budget less than or equal to “Y” (parameterized).
# List the producer name, movie name, box office collection, and budget.
@queries_bp.route("/search_producers", methods=["POST"])
def search_producers():
    """
    Search for American producers based on a minimum box office collection and maximum budget.
    """
    box_office_min = float(request.form["box_office_min"])
    budget_max = float(request.form["budget_max"])

    query = """ SELECT Producers.name AS name, Selected_Movies.name AS movie_name, 
    Selected_Movies.boxoffice_collection, Selected_Movies.budget
    FROM (SELECT r.mpid, p.name 
    FROM Role r JOIN People p ON r.pid = p.id 
    WHERE r.role_name="Producer" AND p.nationality="USA") AS Producers
    JOIN (SELECT mp.id, mp.name, m.boxoffice_collection, mp.budget
    FROM MotionPicture mp JOIN Movie m ON mp.id = m.mpid
    WHERE m.boxoffice_collection >= %s AND mp.budget <= %s) AS Selected_Movies
    ON Producers.mpid = Selected_Movies.id;"""

    results = execute_query(query, (box_office_min, budget_max))
    return render_template("search_producers_results.html", results=results)

# 9. List the people who have played multiple roles in a motion picture where the rating is more than “X” 
# (parameterized). List the person’s and motion picture names, and count the number of roles for that particular picture.
@queries_bp.route("/search_multiple_roles", methods=["POST"])
def search_multiple_roles():
    """
    Search for people who have multiple roles in movies with a rating above a given threshold.
    """
    rating_threshold = float(request.form["rating_threshold"])

    query = """ 
    SELECT Multi_Roles.name, mp.name AS movie_name, Multi_Roles.role_count
    FROM (SELECT r.mpid, p.name, COUNT(*) AS role_count
    FROM Role r JOIN People p ON r.pid = p.id
    GROUP BY r.mpid, r.pid
    HAVING COUNT(*) > 1) AS Multi_Roles
    JOIN MotionPicture mp 
    ON Multi_Roles.mpid = mp.id
    WHERE mp.rating > %s;
    """

    results = execute_query(query, [rating_threshold])
    return render_template("search_multiple_roles_results.html", results=results)

# 10. Find the top 2 rates thriller movies (genre is thriller) that were shot exclusively in Boston. 
# This means that the movie cannot have any other shooting location. List the movie names and their ratings.
@queries_bp.route("/top_thriller_movies_boston", methods=["GET"])
def top_thriller_movies_boston():
    """Display the top 2 thriller movies in Boston based on rating."""

    query = """ 
    SELECT mp.name, mp.rating
    FROM (SELECT mpid, MAX(city) as city
    FROM Location l
    GROUP BY mpid
    HAVING COUNT(DISTINCT(city) = 1)) AS Lonely_Movies
    JOIN MotionPicture mp 
    ON mp.id = Lonely_Movies.mpid
    WHERE Lonely_Movies.city = "Boston" AND 
    mp.id IN (SELECT g.mpid
    FROM Genre g
    WHERE g.genre_name = "Thriller")
    ORDER BY mp.rating DESC
    LIMIT 2;
    """

    results = execute_query(query)
    return render_template("top_thriller_movies_boston.html", results=results)

# 11. Find all the movies with more than “X” (parameterized) likes by users of age less than “Y” (parameterized). 
# List the movie names and the number of likes by those age-group users.
@queries_bp.route("/search_movies_by_likes", methods=["POST"])
def search_movies_by_likes():
    """
    Search for movies that have received more than a specified number of likes,
    where the liking users are below a certain age.
    """
    min_likes = int(request.form["min_likes"])
    max_age = int(request.form["max_age"])

    query = """ 
    SELECT mp.name, COUNT(*) as num_likes
    FROM Likes l JOIN MotionPicture mp 
    ON l.mpid = mp.id
    WHERE l.uemail IN (SELECT u.email
    FROM User u
    WHERE u.age < %s)
    GROUP BY l.mpid
    HAVING COUNT(*) > %s;
    """

    results = execute_query(query, (max_age, min_likes))
    return render_template("search_movies_by_likes_results.html", results=results)

# 12. Find the actors who have played a role in both “Marvel” and “Warner Bros” productions. 
# List the actor names and the corresponding motion picture names.
@queries_bp.route("/actors_marvel_warner", methods=["GET"])
def actors_marvel_warner():
    """
    List actors who have appeared in movies produced by both Marvel and Warner Bros.
    """

    query = """ 
    SELECT p.name, CONCAT(Marvel.name, ", ", Warner.name) AS movie_names
    FROM (SELECT r.pid, mp.name
    FROM Role r JOIN MotionPicture mp ON r.mpid = mp.id
    WHERE r.role_name="Actor" AND mp.production="Marvel") AS Marvel
    JOIN (SELECT r.pid, mp.name
    FROM Role r JOIN MotionPicture mp ON r.mpid = mp.id
    WHERE r.role_name="Actor" AND mp.production="Warner Bros") AS Warner
    ON Marvel.pid = Warner.pid
    JOIN People p
    ON Warner.pid = p.id;
    """

    results = execute_query(query)
    return render_template("actors_marvel_warner.html", results=results)

# 13. Find the motion pictures with a higher rating than the average rating of all comedy (genre) motion pictures. 
# Show the names and ratings in descending order of ratings.
@queries_bp.route("/movies_higher_than_comedy_avg", methods=["GET"])
def movies_higher_than_comedy_avg():
    """
    Display movies whose rating is higher than the average rating of comedy movies.
    """

    query = """ 
    SELECT mp.name, mp.rating
    FROM MotionPicture mp
    WHERE mp.rating > (SELECT AVG(mp.rating)
    FROM Genre g JOIN MotionPicture mp
    ON g.mpid = mp.id
    WHERE g.genre_name = "Comedy"
    GROUP BY g.genre_name)
    ORDER BY rating DESC;
    """

    results = execute_query(query)
    return render_template("movies_higher_than_comedy_avg.html", results=results)

# 14. Find the top 5 movies with the most people playing a role in that movie. 
# Show the movie name, people count, and role count for the movies.
@queries_bp.route("/top_5_movies_people_roles", methods=["GET"])
def top_5_movies_people_roles():
    """
    Display the top 5 movies that involve the most people and roles.
    """

    query = """ 
    SELECT mp.name, Counts.people_count, Counts.role_count
    FROM (SELECT mpid, COUNT(DISTINCT(pid)) AS people_count, COUNT(DISTINCT(role_name)) AS role_count
    FROM Role r
    GROUP BY mpid) Counts JOIN MotionPicture mp
    ON Counts.mpid = mp.id
    ORDER BY Counts.people_count DESC, Counts.role_count DESC
    LIMIT 5;
    """

    results = execute_query(query)
    return render_template("top_5_movies_people_roles.html", results=results)

# 15. Find actors who share the same birthday. 
# List the actors’ names (actors 1 and 2) and their common birthday.
@queries_bp.route("/actors_with_common_birthday", methods=["GET"])
def actors_with_common_birthday():
    """
    Find pairs of actors who share the same birthday.
    """

    # >>>> TODO 15: Find actors who share the same birthday. <<<<
    #               List the actor names (actor 1, actor 2) and their common birthday.

    query = """ 
    WITH Actors AS (SELECT DISTINCT p.id, p.name, p.dob
    FROM People p JOIN Role r
    ON p.id = r.pid
    WHERE r.role_name="Actor")
    SELECT a1.name, a2.name, a1.dob
    FROM Actors a1, Actors a2
    WHERE a1.dob = a2.dob AND a1.id < a2.id;
    """

    results = execute_query(query)
    return render_template("actors_with_common_birthday.html", results=results)