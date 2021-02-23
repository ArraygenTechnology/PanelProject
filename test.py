import pdfkit
options = {
   'page-size': 'Letter',
   'margin-top': '0.75in',
   'margin-right': '0.75in',
   'margin-bottom': '0.5in',
   'margin-left': '0.75in',
   'header-left': 'something',
   'header-right': '[section]',
   'footer-right': '[page]',
   }

pdfkit.from_url("https://stackoverflow.com/questions/50779742/pdfkit-formatting-header-footers", "test.pdf", options=options)