from flask import Flask, request, send_file, render_template_string
import qrcode
import io
import os
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER = 'qr_codes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DOMAIN = "https://linking.cards/"

@app.route('/')
def index():
    return render_template_string('''
    <!doctype html>
    <html lang="en">
      <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <!-- Bootstrap CSS -->
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <title>QR Code Generator</title>
      </head>
      <body>
        <div class="container mt-5">
          <h1 class="text-center">QR Code Guru 🧘</h1>
          <form action="/generate" method="post">
            <div class="form-group">
              <input type="text" name="link" class="form-control" placeholder="Enter URL ending" required>
            </div>
            <div class="form-group">
              <label for="qr_color">QR Code Color:</label>
              <input type="color" id="qr_color" name="qr_color" value="#000000" class="form-control">
            </div>
            <button type="submit" class="btn btn-primary">Generate QR Code</button>
          </form>
          <form action="/generate_multiple" method="post" class="mt-4">
            <div id="links">
              <div class="form-group">
                <input type="text" name="links" class="form-control" placeholder="Enter URL ending" required>
              </div>
            </div>
            <div class="form-group">
              <label for="qr_color_multi">QR Code Color:</label>
              <input type="color" id="qr_color_multi" name="qr_color_multi" value="#000000" class="form-control">
            </div>
            <button type="button" class="btn btn-secondary" onclick="addLink()">Add Another Link</button>
            <button type="submit" class="btn btn-primary">Generate Multiple QR Codes</button>
          </form>
        </div>
        <script>
          function addLink() {
            var newLink = '<div class="form-group"><input type="text" name="links" class="form-control" placeholder="Enter URL ending" required></div>';
            document.getElementById('links').insertAdjacentHTML('beforeend', newLink);
          }
        </script>
      </body>
    </html>
    ''')

@app.route('/generate', methods=['POST'])
def generate_qr():
    link_ending = request.form['link']
    qr_color = request.form['qr_color']
    full_link = DOMAIN + link_ending
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    qr.add_data(full_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color=qr_color, back_color="transparent")

    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)

    return send_file(buf, mimetype='image/png', download_name=f'{link_ending}.png')

@app.route('/generate_multiple', methods=['POST'])
def generate_multiple_qrs():
    links = request.form.getlist('links')
    qr_color = request.form['qr_color_multi']
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for link_ending in links:
            full_link = DOMAIN + link_ending
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=0,
            )
            qr.add_data(full_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color=qr_color, back_color="transparent")

            img_buffer = io.BytesIO()
            img.save(img_buffer)
            img_buffer.seek(0)
            zip_file.writestr(f'{link_ending}.png', img_buffer.read())

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='qr_codes.zip')

if __name__ == '__main__':
    app.run(debug=True)
