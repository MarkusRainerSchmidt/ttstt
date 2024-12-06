# ttstt - TableTop Simulator TerrainTool

## Installation

Install Python (at least version 3.11) and make sure to add it to your path.
Then run in a terminal:

    pip install git+https://github.com/MarkusRainerSchmidt/ttstt

## Running the Tool

### Starting the Server

In a terminal, navigate to the folder you want to run the server in.
Make sure this folder has two subfolders: `textures`, and `export`.
Then run:

    ttstt

The server should print something into the terminal that ends on something like this:

     * Serving Flask app 'ttstt.main'
    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
     * Running on http://127.0.0.1:5000
    Press CTRL+C to quit

Note down the URL the server is running on. In this example it is `http://127.0.0.1:5000`.

### Connecting to the Server

To connect to the server in TableTop Simulator, open a game, then go to `Modding` -> `Scripting`.
There copy the content of the `curr_script.lua` @todo into the `Lua` box.
Further, copy the content of the `curr_ui.xml` @todo into the `UI` box. Then hit `Save & Play`.

A box should appear at the bottom left of your screen. 
Paste the URL you saved from the server output into the box and hit connect.

A small rectangle of terrain should appear the the GUI of the terrain tool should load.

## Configuring the Tool

### Textures

Inside the `textures` folder you can place .png files which will be loaded when you start the server.
The alphabetically first .png file will be used as the default texture, 
hence it is recommended to prefix one image with `0_` to select it as default.

### Random Generation

By placing a file called `random_conf.json` in the folder where you run the server,
you can configure the random generation (advanced button).
The file should look something like @todo.