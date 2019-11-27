import functools
import json
from . import jc
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/map', methods=('GET', 'POST'))
def map():
    if request.method == 'POST':
        inputjson = request.form['inputjson']
        outputformat = request.form['outputformat']
        error = None
        print(len(inputjson), "===============")
        if not inputjson or len(inputjson.strip()) == 0:
            error = 'input is required.'
        elif not outputformat or len(inputjson.strip()) == 0:
            error = 'output is required.'

        if error is None:
            print("compose json")
            inputjson=json.loads(inputjson)
            outputformat=json.loads(outputformat)
            rj = jc.ComposeJson(inputjson, outputformat)
            print(rj.autojson)
            outputjson = rj.load_output_template()

            # return redirect(url_for('auth.map'))
            print(outputjson)
            return render_template('map.html', outputjson=(outputjson), inputjson=json.dumps(inputjson), outputformat=json.dumps(outputformat))

        flash(error)

    inputjson="""{"data":{"songs":[{"album":"petta","composer":"ani","year":"2019","song_name":"kalyanam","movie":{"name":"petta"},"actor":{"name":"rajini"},"award":["NTCA","OSCAR","IFFA"]},{"album":"petta","composer":"ani","year":"2019","song_name":"petta","movie":{"name":"petta"},"actor":{"name":"rajini"},"award":["NTCA","OSCAR","IFFA"]},{"album":"thegidi","composer":"nivas","year":"2016","song_name":"vinmeen","movie":{"name":"thegidi"},"actor":{"name":"ashok"},"award":["NTCA","IFFA"]},{"album":"thegidi","composer":"nivas","year":"2016","song_name":"nethane","movie":{"name":"thegidi"},"actor":{"name":"ashok"},"award":["NTCA","IFFA"]},{"album":"Maattrraan","composer":"harria","year":"2012","song_name":"theye","movie":{"name":"Maattrraan"},"actor":{"name":"surya"},"award":["IFFA"]},{"album":"Maattrraan","composer":"harria","year":"2012","song_name":"nani koni","movie":{"name":"Maattrraan"},"actor":{"name":"surya"},"award":["IFFA"]}]}}"""
    outputformat="""{"data|songs|*|movie|name":["data|songs|*|song_name"]}"""
    return render_template('map.html', inputjson=inputjson, outputformat=outputformat)