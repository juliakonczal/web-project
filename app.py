from flask import Flask, redirect, url_for, render_template, request
from werkzeug.utils import secure_filename
import tempfile
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

@app.route("/")
@app.route("/stronaglowna")
def stronaglowna():
    """Returns "strona glowna" page"""
    return render_template("stronaglowna.html")

@app.route("/kontakt")
def kontakt():
    """Returns "kontakt" page"""
    return render_template("kontakt.html")

@app.route("/analiza")
def analiza():
    """Returns "analiza" page"""
    return render_template("analiza.html")

def allowed_file(filename):
    """Checks if file extension is .csv"""
    if ".csv" in filename:
        return True
    return False
    
def get_path(filename):
    file_path = os.path.join(tempfile.gettempdir(), filename)    
    return file_path

@app.route('/analiza1', methods=['GET', 'POST'])   
def analiza1():
    """After uploading file, it checks if file is correct and creates lists with variables"""
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = get_path(filename)
            file.save(file_path)
            with open(file_path, 'r') as f:
                data = pd.read_csv(f)
            variable_list = [] #nazwy kolumn
            variable_list_cat = [] #zmienne kategoryczne
            variable_list_con = [] #zmienne ciągłe
            second_line = list(data.iloc[1]) #druga lista, dzieki ktorej sprawdzimy ktore ciagle ktore kategoryczne
            for row in data:
                variable_list.append(row)
            #teraz będę sprawdzać, które kolumny to ciągłe, a które kategoryczne
            for i in range(len(second_line)):
                try:
                    float(second_line[i])
                    variable_list_con.append(variable_list[i])
                except:
                    variable_list_cat.append(variable_list[i])

            return render_template("analiza1.html", variable_list_con=variable_list_con, variable_list_cat = variable_list_cat, filename = filename)
    warning = "Plik powinien mieć rozszerzenie .csv !"
    return render_template("analiza.html", warning=warning)


def plotting(groups, var1, var2, mean_val1, mean_val2, xlabel, ylabel, title):
    """Creates a chart"""
    fig, ax = plt.subplots()
    names = []
    for name, group in groups:
        plt.scatter(group[var1], group[var2], marker="o", label=name)
        names.append(name)
    # plt.scatter(mean_val1, mean_val2, marker="D", c="black", linewidths=4)
    for i in range(len(mean_val1)):
        # ax.annotate("srednie", (mean_val1[i], mean_val2[i]))
        plt.scatter(mean_val1, mean_val2, marker="o", c="black")
        ax.annotate('średnie dla '+str(names[i]), xy=(mean_val1[i],mean_val2[i]), xytext=(mean_val1[i]-0.4,mean_val2[i]+0.5),
        bbox=dict(boxstyle="round4", fc="w"),
                 arrowprops=dict(arrowstyle="->"))
        # ax.text(mean_val1[i],mean_val2[i], str(round(mean_val1[i], 3))+", "+str(round(mean_val2[i], 3)), color='black', bbox=dict(facecolor='white', edgecolor='black'))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    return fig

def translate_image_to_base64(fig):
    """Get Figure object and return its base64 representation"""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    b_64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close(fig)
    return f"data:image/png;base64,{b_64}"

@app.route('/analiza2', methods = ['GET','POST'])
def submitForm():
    """Checks selected values and creates table and chart for next subpage"""
    if request.method == 'POST':
        selectValue1 = request.form.get('var1')
        selectValue2 = request.form.get('var2')
        selectValue3 = request.form.get('var3')
        filename = request.form.get('filename')

        with open(get_path(filename), 'r') as f:
            data = pd.read_csv(f)

        d = data.groupby([selectValue3])[selectValue1, selectValue2].mean()
        tables =[d.to_html(classes='data', header="true")]

        mean_val1 = d[selectValue1].tolist()
        mean_val2 = d[selectValue2].tolist()

        groups = data.groupby(selectValue3)
        fig = plotting(groups, selectValue1, selectValue2, mean_val1, mean_val2, selectValue1, selectValue2, "Wykres na podstawie pliku "+str(filename))
        draw = translate_image_to_base64(fig)

        return render_template("analiza2.html", tables=tables, drawing=draw)
    return redirect(url_for("analiza1"))


if __name__ == "__main__":
    app.run()