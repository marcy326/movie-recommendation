# Movie Recommendation System

This project is a sample application for building a movie recommendation system. When users input ratings for specific movies, the system recommends similar movies.

## Installation

1. Clone this repository:

```bash
git clone https://github.com/marcy326/movie-recommendation.git
```

2. Navigate to the project directory:

```bash
cd movie-recommendation
```

3. Use Docker Compose to launch the application:

```bash
docker compose up --build
```

4. Access the application in your browser at the following URL:

```URL
http://localhost:8501
```

## Usage
1. Access the application in your browser.
1. Enter the user_id and other parameters.
1. Click the "Get Recommendation" button to display recommended movies.


## Technical Details
- Python: Used for backend development
- FastAPI: Used for creating API endpoints
- Streamlit: Used for frontend development
- SQLAlchemy: Used for database operations
- MySQL: Used as the database management system
- Docker Compose: Used for containerization and launching the application

## License
MIT License