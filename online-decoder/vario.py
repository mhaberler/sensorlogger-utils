from flask import render_template, request, make_response, send_file, Blueprint
import io
import os
from werkzeug.utils import secure_filename
from util import allowed_file, make_numeric
import pandas
import csv
from gentp import Teleplot
import numpy

vario = Blueprint("vario", __name__, template_folder="templates")


def variolog_to_dataframe(input):
    df = pandas.read_csv(input, delimiter=";")

    # drop rows with invalid date
    t = df[df["Date"] != "00/00/2000"]
    t = t[t["Date"] != "00/00/00"]

    # drop rows with invalid time
    t = t[t["Time"] != "00:00:00"]

    # combine Date and time into new field
    t["timestamp"] = pandas.to_datetime(
        t["Date"] + " " + t["Time"], dayfirst=True
    ).astype(int)

    # divide the resulting integer by the number of nanoseconds in a second
    t["timestamp"] = t["timestamp"].div(10**9)

    # drop useless Date and Time
    t = t.drop(columns=["Date", "Time"])

    return t


def generate(df, destfmt, options):
    if "teleplot" in destfmt:
        tp = Teleplot()
        for _, row in df.iterrows():
            ts = row["timestamp"]
            for name in df.columns:
                if name == "timestamp":
                    continue
                value = row[name]
                v = make_numeric(value)
                if not v:
                    continue
                if numpy.isnan(v):
                    continue
                tp.addSample(name, v, ts)
        return ("_vario2tp.json", tp.toJson().encode("utf8"))
    if "csv" in destfmt:
        s = df.to_csv(sep=";", quoting=csv.QUOTE_NONNUMERIC) #,  quotechar="'")
        return ("_sanitized.csv", s.encode("utf8"))


@vario.route("/vario", methods=["GET", "POST"])
def entry():
    if request.method == "GET":
        return render_template("vario.html")
    if request.method == "POST":
        destfmt = request.form.getlist("destfmt")
        options = request.form.getlist("options")
        files = request.files.getlist("files")
        for file in files:
            fn = secure_filename(file.filename)
            if fn and allowed_file(fn, ["csv"]):
                dataframe = variolog_to_dataframe(file)
                (ext, output) = generate(dataframe, destfmt, options)
                buffer = io.BytesIO()
                buffer.write(output)
                buffer.seek(0)
                base, _ = os.path.splitext(fn)
                response = make_response(
                    send_file(
                        buffer,
                        download_name=base + ext,
                        as_attachment=True,
                    )
                )
                return response
            else:
                return render_template("vario.html")
