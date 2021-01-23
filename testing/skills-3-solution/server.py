from flask import Flask, redirect, request, render_template, session
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined


app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
app.jinja_env.auto_reload = True

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Getting our list of MOST LOVED MELONS
MOST_LOVED_MELONS = {
    'cren': {
        'img': 'http://www.rareseeds.com/assets/1/14/DimRegular/crenshaw.jpg',
        'name': 'Crenshaw',
        'num_loves': 584,
    },
    'jubi': {
        'img': 'http://www.rareseeds.com/assets/1/14/DimThumbnail/Jubilee-Watermelon-web.jpg',
        'name': 'Jubilee Watermelon',
        'num_loves': 601,
    },
    'sugb': {
        'img': 'http://www.rareseeds.com/assets/1/14/DimThumbnail/Sugar-Baby-Watermelon-web.jpg',
        'name': 'Sugar Baby Watermelon',
        'num_loves': 587,
    },
    'texb': {
        'img': 'http://www.rareseeds.com/assets/1/14/DimThumbnail/Texas-Golden-2-Watermelon-web.jpg',
        'name': 'Texas Golden Watermelon',
        'num_loves': 598,
    },
}

# YOUR ROUTES GO HERE


# Homepage
@app.route('/')
def show_homepage():
    """Show homepage with form for user's name. If name already stored, redirect."""

    if 'name' in session:
        return redirect('/top-melons')

    return render_template('homepage.html')


@app.route('/get-name')
def get_name():
    """Get name from homepage form and store name in session."""

    name = request.args.get('name')
    session['name'] = name
    return redirect('/top-melons')


@app.route('/top-melons')
def show_top_melons():
    """Show list of top melons."""

    if 'name' not in session:
        return redirect('/')

    return render_template('top_melons.html', melons=MOST_LOVED_MELONS)


@app.route('/love-melon', methods=['POST'])
def love_melon():
    """Add one to the melon love count."""

    melon = request.form.get('melon')
    MOST_LOVED_MELONS[melon]['num_loves'] += 1
    return render_template('thank-you.html')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
