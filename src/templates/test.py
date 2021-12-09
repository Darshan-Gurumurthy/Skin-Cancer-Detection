if preds != None:
    res = render_template('result.html', result=result) #generating pdf
    responsestring  = pdf.from_file(res,False)
    response = make_response(responsestring)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=output.pdf'


@app.route("/getpdf", methods=["POST", "GET"])
def getpdf():
    if request.method == 'POST':

    return '''Click here to open the
    <a href="http://localhost:5000/static/uploads/demo4.pdf">pdf</a>.'''

rendered = render_template('result.html', result=result)
pdf  = pdfkit.from_file(rendered,False)
response = make_response(pdf)
response.headers['Content-Type'] = 'application/pdf'
response.headers['Content-Disposition'] = 'inline;filename=output.pdf'


#res = pdfkit.from_file(''','demo.pdf')
#options = {'enable-local-file-access': None}   ,options=options
pdf  = pdfkit.from_file('templates/temp.html',False)

# Optional: add a timestamp to the generated file.
created_on
filename = f"Filename ({created_on})"
file = io.BytesIO(pdf)
return send_file(file,attachment_filename=filename,mimetype='application/pdf',as_attachment=True,cache_timeout=-1)

def GenPDF():
    responsestring  = pdf.from_file('result.html',False)
    response = make_response(responsestring)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=output.pdf'
    return response
