# Auto BoD

This application let's you automatically execute consecutive awakes on your desired item based on the list of stats that you desired.

## Usage

In order to properly use this simple application to automatically awake items, follow theses steps.
_Note: This is assuming that the application is already built_

1. Open your FlyffU game and the BoD window
2. Identify the coordinates enclosing the result awake and the start button using MS Paint and take note of it
3. Open **/dist** folder and run the **bod-auto.exe**
4. When the window prompts asking for the _region_, enter the coordinates taken earlier
5. Another window prompt will appear asking for the stats you desired for your item
	1. It could be a single stat or a list of stat by separating it with comma
	2. Make sure with no space for now (E.g. INT,STA,DEX,CastingSpeed)
6. The app will now automatically click the **start** button and start the automation.

## Development

1. Make sure Python is already installed
2. Execute: pip install pyautogui pytesseract pillow opencv-python
3. Download https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe
	1. Install the Tesseract-OCR under this project's folder. E.g. **/tesseract**
	2. The **/tesseract** must contain all of the contents without any additional parent folder folder. E.g. **/tesseract/tesseract.exe**
4. Execute build-app.bat
	1. This will generate the **/dist** folder containing the **bod-auto.exe**


## Improvement

- [ ] App should be able to identify the BoD window without asking for its coordinates in the screen
- [ ] Proper UI for desired stats with its value
