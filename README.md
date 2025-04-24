# Dataextraction

## For pdf extraction from website 
How to use downloader.py :-  Download selenium and adjust the code such that it works on windows (the code is according to MAC OS) and also download other packages.  It open the website and enters the date and the unit and police station(if it does not work due to some bug in website it will refresh and enter the details and download the pdfs)  

#### some imp points:  
if you run this code use the date formatting which I have set in the code  use tell time intervals short so that you don’t have to navigate between pages

This code already set the table to max 50

#### What you can do to download all pdf: run another script which runs this file and downloads the files from all units and all police station from smaller interval of dates (remember BNS is applied from 1st July 2024)


## For details extraction from pdf
How to use pdf_try.py :-  Download the packages and give the address the pdf and it will extract the details of the First Information contents (म खब तकग). I haven’t written the extraction for the sections from the table. The code also has parts to remove the headers and footers


