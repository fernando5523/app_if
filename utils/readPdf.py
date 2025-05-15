# import pandas, tabula

# class pdfRead:
#     def readHeadPdf(self, ruc, coordinates, urlFile):

#         __pdfData = tabula.read_pdf(urlFile, area=coordinates, output_format="dataframe", pages=1, stream=True)
#         if __pdfData is not None and __pdfData[0].empty and ruc in __pdfData[0].columns:
#             __responsePDF = pandas.concat(__pdfData, ignore_index=True)
#             __responsePDF = {"RUC": str(__responsePDF.columns[0]), "URLFILE": urlFile}
#             return __responsePDF
#         else:
#             return "errorPDF"