# googleNotesToThermal
Use Google Notes UI to manipulate lists or notes and use their labels as triggers to print them with an Epson TM-T88V. Confirmed working on NanoPiNeo running Armbian! See [link](https://github.com/ijjy303/googleNotesToThermal/blob/main/armbian-scripts/armbian-install-script.sh) for installation instructions

<img src="https://github.com/ijjy303/googleNotesToThermal/blob/3bbf7e65e94f214db3cfaf3b7dff64e48ca312dd/examples/final.gif" width="604"> 

## Main function
- Use and Assign labels to notes on Google Keep Notes mobile app in order to trigger specific events.
- Can trigger any event or script running on 'listener' GkeepAPI python script
- Label a note, 'print-me' and it will be sent to thermal printer
  - Will [essentially] print note as efficiently as possible. ie: As many checkboxes/characters on a single line without sperating one checkbox onto multiple lines
- Label a note 'X' to reorganize it and create/upload a copy of it to Google Keeps app. Example: [link](https://github.com/ijjy303/googleNotesToThermal/blob/main/examples/note2ThermSS.jpg) ```createOrganizedCopy()``` 
- Label a note 'grocery-list' and it will be reorganize it by aisle and alphabetically to convert an otherwise random grocery list into the most efficient buying route
```getNotesWith(label='grocery-list', ordered='grocery')```

## Requirements
- keyring
- gkeepapi
- escpos
- requests (if saving images locally that were stored in a note)

## In Action:
<img src="https://github.com/ijjy303/googleNotesToThermal/blob/3bbf7e65e94f214db3cfaf3b7dff64e48ca312dd/examples/note2thermNPiNeo.jpg" width="525"> <img src="https://github.com/ijjy303/googleNotesToThermal/blob/3bbf7e65e94f214db3cfaf3b7dff64e48ca312dd/examples/optimal-route.jpg" width="395">

## Credit
- gkeepapi library documentation: https://gkeepapi.readthedocs.io/en/latest/
- escpos library documentation: https://python-escpos.readthedocs.io/en/latest/
- Epson TM-T88V driver and installation on debian system: https://github.com/ijjy303/epson-tm-t88v-driver
- This tech reference PDF: https://files.support.epson.com/pdf/pos/bulk/tm-t88v-dt_linux_e_trg_revb.pdf
- This guys guide, a bit more info than necessary but vital info for testing on Windows machine: https://nyorikakar.medium.com/printing-with-python-and-epson-pos-printer-fbd17e127b6c

## TODO:
Add Windows installation instructions
