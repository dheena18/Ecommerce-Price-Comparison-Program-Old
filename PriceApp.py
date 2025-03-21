import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup
import pandas as pd
import webbrowser

product = ""
flipData = {}
amzData = {}
amzProductLink = ""
flipProductLink = ""


class PriceApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("CompareYourProduct")
        masterWin = {"width": 1000, "height": 700, "xPos": 250, "yPos": 50}
        self.geometry(
            "{}x{}+{}+{}".format(
                masterWin["width"],
                masterWin["height"],
                masterWin["xPos"],
                masterWin["yPos"],
            )
        )
        self.config(bg="white")

        # Bold fonts
        self.titleFont = tkfont.Font(family="Helvetica", size=30, weight="bold")
        self.largeBoldFont = tkfont.Font(family="Helvetica", size=15, weight="bold")
        self.mediumBoldFont = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.smallBoldFont = tkfont.Font(family="Helvetica", size=10, weight="bold")

        # Normal fonts
        self.largeFont = tkfont.Font(family="Helvetica", size=15)
        self.mediumFont = tkfont.Font(family="Helvetica", size=12)
        self.smallFont = tkfont.Font(family="Helvetica", size=10)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self, bg="black")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (EntryScreen, SelectScreen):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
            # print(page_name)

        self.show_frame("EntryScreen")

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        frame.tkraise()


class EntryScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        frame = tk.Frame(
            self,
            bg="black",
            height=700,
            width=1000,
            bd=1,
            relief=tk.FLAT,
            borderwidth=5,
        )
        # frame.pack(fill=tk.X, padx=5, pady=5)
        frame.place(x=0, y=0)

        container = tk.Frame(
            self,
            bg="#333",
            height=400,
            width=500,
            bd=1,
            relief=tk.GROOVE,
            borderwidth=5,
        )
        container.place(x=250, y=150)

        titleLabel = tk.Label(
            container,
            text="CompareYourProduct",
            font=controller.titleFont,
            bg="#333",
            fg="white",
        )
        titleLabel.place(x=35, y=30)

        titleDescriptionLabel = tk.Label(
            container,
            text="A price comparison engine",
            font=controller.mediumBoldFont,
            bg="#333",
            fg="white",
        )
        titleDescriptionLabel.place(x=135, y=100)

        enterProdNameLabel = tk.Label(
            container,
            text="Enter Product Name : ",
            font=controller.largeBoldFont,
            bg="#333",
            fg="white",
        )
        enterProdNameLabel.place(x=10, y=180)

        self.userInput = tk.StringVar()

        self.prodNameEntry = tk.Entry(
            container, width=25, font=controller.mediumFont, textvariable=self.userInput
        )
        self.prodNameEntry.place(x=225, y=183)
        self.prodNameEntry.focus()

        clearEntryButton = tk.Button(
            container,
            text="✕",
            bg="white",
            fg="black",
            font=controller.smallFont,
            command=self.__clearEntryText,
        )
        clearEntryButton.place(x=458, y=180)

        submitButton = tk.Button(
            container,
            text="Check prices",
            width=12,
            height=1,
            bg="green",
            fg="white",
            font=controller.smallBoldFont,
            command=self.__submit,
        )
        submitButton.place(x=80, y=300)

        cancelButton = tk.Button(
            container,
            text="Exit",
            width=12,
            height=1,
            bg="red",
            fg="white",
            font=controller.smallBoldFont,
            command=controller.destroy,
        )
        cancelButton.place(x=320, y=300)
        """ 
        #0099ff blue
        #ffcc00 yellow
        #ff0000 red
        """

    def __getFlipRequest(self):
        data = {"products": [], "prices": [], "ratings": [], "url": []}

        url = "https://www.flipkart.com/search?q="
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
        }
        products_class = "_31qSD5"

        # search_input = input("Enter product name : ").replace(" ", "+")
        print("Flipkart getting userInput...")
        global product
        search_input = product
        print("Flipkart Product is : ", search_input)

        link = url + search_input

        source = requests.get(link, headers=headers)
        content = source.text
        soup = BeautifulSoup(content, "lxml")

        for a in soup.findAll("a", href=True, attrs={"class": products_class}):
            data["url"].append("https://flipkart.com" + a["href"])

            try:
                name = a.find("div", attrs={"class": "_3wU53n"})
                data["products"].append(name.text[:60])

                try:
                    price = a.find("div", attrs={"class": "_1vC4OE _2rQ-NK"})
                    data["prices"].append(
                        int(price.text.replace("₹", "").replace(",", ""))
                    )
                except AttributeError:
                    data["prices"].append("N.A")

                try:
                    rating = a.find("div", attrs={"class": "hGSR34"})
                    data["ratings"].append(rating.text)
                except AttributeError:
                    data["ratings"].append("N.A")

            except AttributeError:
                continue

        df = pd.DataFrame(
            {
                "Select Product": data["products"],
                "Price": data["prices"],
                "Rating": data["ratings"],
                "Link": data["url"],
            }
        )
        df.to_csv("flip.csv", index=False, encoding="utf-8")
        return data

    def __getAmzRequest(self):
        data = {"products": [], "prices": [], "ratings": [], "url": []}

        url = "https://www.amazon.in/s?k="
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
        }
        products_class_rows = "sg-col-4-of-12 sg-col-8-of-16 sg-col-16-of-24 sg-col-12-of-20 sg-col-24-of-32 sg-col sg-col-28-of-36 sg-col-20-of-28"
        products_class_boxes = "sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item s-asin sg-col-4-of-28 sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32"

        # search_input = input("Enter product name : ").replace(" ", "+")
        print("Amazon getting userInput...")
        global product
        search_input = product
        print("Amazon Product is : ", search_input)

        link = url + search_input + "&ref=nb_sb_noss_2"

        source = requests.get(link, headers=headers)
        content = source.text
        soup = BeautifulSoup(content, "lxml")

        products = soup.findAll("div", attrs={"class": products_class_rows})

        # for i in range(1, len(products) // 4):
        #     print(products[i])
        # print(len(products))
        # print(type(products))

        # print(products[1])

        if len(products) != 1:
            for prod in products:
                try:
                    name = prod.find(
                        "span",
                        attrs={"class": "a-size-medium a-color-base a-text-normal"},
                    )
                    data["products"].append(name.text[:60])

                    try:
                        price = prod.find("span", attrs={"class": "a-price-whole"})
                        data["prices"].append(int(price.text.replace(",", "")))
                    except AttributeError:
                        data["prices"].append("N.A")

                    try:
                        rating = prod.find("span", attrs={"class": "a-icon-alt"})
                        data["ratings"].append(rating.text[:3])
                    except AttributeError:
                        data["ratings"].append("N.A")

                    try:
                        product_url = prod.find(
                            "a", attrs={"class": "a-link-normal a-text-normal"}
                        )
                        data["url"].append("http://www.amazon.in" + product_url["href"])
                    except AttributeError:
                        data["url"].append("N.A")

                except AttributeError:
                    continue
        else:
            # products not in row form
            # add for loop for scraping product boxes
            data["products"].append("No products available")
            data["prices"].append("NA")
            data["ratings"].append("NA")
            data["url"].append("NA")

        df = pd.DataFrame(
            {
                "Select Product": data["products"],
                "Price": data["prices"],
                "Rating": data["ratings"],
                "Link": data["url"],
            }
        )
        df.to_csv("amz.csv", index=False, encoding="utf-8")

        return data

    def __submit(self):
        global product, flipData, amzData
        product = self.userInput.get()

        flipData = self.__getFlipRequest()
        # print(flipData["products"])
        amzData = self.__getAmzRequest()
        # print(amzData["products"])

        # SelectScreen.__showOptions(self=SelectScreen)
        self.controller.show_frame("SelectScreen")

    def __clearEntryText(self):
        self.prodNameEntry.delete(0, tk.END)


class SelectScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Black frame
        frame = tk.Frame(
            self,
            bg="#222",
            height=700,
            width=1000,
            bd=1,
            relief=tk.FLAT,
            borderwidth=5,
        )
        frame.place(x=0, y=0)

        # Image Processing
        backImage = Image.open("./assets/back-button.png")
        backLogo = ImageTk.PhotoImage(backImage)
        # small = amzLogo.subsample(3, 3)

        def backButton():
            # self.controller.show_frame("EntryScreen")
            self.destroy()

        # Back button
        backButton = tk.Button(
            frame,
            # font=controller.mediumBoldFont,
            image=backLogo,
            bg="#222",
            borderwidth=0,
            command=backButton,
        )
        backButton.place(x=50, y=20)

        titleLabel = tk.Label(
            frame,
            text="CompareYourProduct",
            font=controller.titleFont,
            bg="black",
            fg="white",
        )
        titleLabel.place(x=280, y=20)

        """ FLIPKART AREA """
        # Flipkart Frame
        flipFrame = tk.Frame(
            frame,
            # bg="#ffffb3",     light blue
            bg="#0099ff",  # blue
            height=250,
            width=900,
            bd=1,
            relief=tk.RIDGE,
            borderwidth=5,
        )
        flipFrame.place(x=50, y=100)

        # Flipkart Results label
        flipTitleLabel = tk.Label(
            flipFrame,
            text="Flipkart Results : ",
            font=controller.largeBoldFont,
            bg="black",
            fg="white",
        )
        flipTitleLabel.place(x=20, y=20)

        # Flipkart product label
        flipProductLabel = tk.Label(
            flipFrame,
            text="Product : ",
            font=controller.mediumBoldFont,
            bg="black",
            fg="white",
        )
        flipProductLabel.place(x=50, y=100)

        # Price label
        flipPriceLabel = tk.Label(
            flipFrame,
            text="Price : ",
            font=controller.mediumBoldFont,
            bg="black",
            fg="white",
        )
        flipPriceLabel.place(x=50, y=150)

        # Rating Label
        flipRatingLabel = tk.Label(
            flipFrame,
            text="Rating : ",
            font=controller.mediumBoldFont,
            bg="black",
            fg="white",
        )
        flipRatingLabel.place(x=300, y=150)

        # Reading the saved CSV file
        flipColnames = ["Product", "Price", "Rating", "Link"]
        flipData = pd.read_csv("flip.csv", names=flipColnames)

        # Assigning columns from CSV to variables
        flipProducts = flipData.Product.tolist()
        flipPrices = flipData.Price.tolist()
        flipRatings = flipData.Rating.tolist()
        flipLinks = flipData.Link.tolist()

        def onFlipOptionSelected(*args):
            # Getting the product selected and its index in the products list
            selectedProduct = flipOptionVar.get()
            indexOfSelectedProduct = flipProducts.index(selectedProduct)

            # Getting price from the prices list and setting the label text
            priceOfSelectedProduct = str(flipPrices[indexOfSelectedProduct])
            flipPriceLabel.config(text="Price : " + priceOfSelectedProduct)

            # Getting rating from the ratings list and setting the label text
            ratingOfSelectedProduct = flipRatings[indexOfSelectedProduct]
            flipRatingLabel.config(text="Rating : " + ratingOfSelectedProduct)

            # Getting link from the links list
            global flipProductLink
            flipProductLink = str(flipLinks[indexOfSelectedProduct])

        # Variable which points to the selected option in dropdown menu
        flipOptionVar = tk.StringVar(flipFrame)

        # Monitor flipOptionVar for any changes in write mode and call onFlipOptionSelected
        """ trace(mode, callback) """
        flipOptionVar.trace("w", onFlipOptionSelected)

        # Setting the first element of flipProducts as selected option
        flipOptionVar.set(flipProducts[0])

        # Products dropdown menu
        """ tk.OptionMenu(master, variable, values) """
        flipOptions = tk.OptionMenu(flipFrame, flipOptionVar, *flipProducts)
        flipOptions.place(x=180, y=97)

        # Image Processing
        flipImage = Image.open("./assets/flipkart-trans.png")
        flipLogo = ImageTk.PhotoImage(flipImage)
        # small = flipLogo.subsample(3, 3)

        # Opening web page
        new = 1

        def visitFlip(url):
            print("Button Pressed")
            webbrowser.open(url, new=new)

        # Flipkart visit Label
        flipVisitLabel = tk.Label(
            flipFrame,
            text="Visit Page : ",
            font=controller.mediumBoldFont,
            bg="black",
            fg="white",
        )
        flipVisitLabel.place(x=550, y=70)

        # Visit page button
        flipVisitButton = tk.Button(
            flipFrame,
            font=controller.mediumBoldFont,
            image=flipLogo,
            bg="white",
            command=lambda: visitFlip(flipProductLink),
        )
        flipVisitButton.place(x=550, y=100)

        """ AMAZON AREA """
        # Amazon Frame
        amzFrame = tk.Frame(
            frame,
            # bg="#9fbfdf",  light yellow
            bg="#ffcc00",
            height=250,
            width=900,
            bd=1,
            relief=tk.RIDGE,
            borderwidth=5,
        )
        amzFrame.place(x=50, y=400)

        # Amazon Results label
        amzTitleLabel = tk.Label(
            amzFrame,
            text="Amazon Results : ",
            font=controller.largeBoldFont,
            bg="black",
            fg="white",
        )
        amzTitleLabel.place(x=20, y=20)

        # Amazon product label
        amzProductLabel = tk.Label(
            amzFrame,
            text="Product : ",
            font=controller.mediumBoldFont,
            bg="black",
            fg="white",
        )
        amzProductLabel.place(x=50, y=100)

        # Price Label
        amzPriceLabel = tk.Label(
            amzFrame,
            text="Price : ",
            font=controller.mediumBoldFont,
            bg="black",
            fg="white",
        )
        amzPriceLabel.place(x=50, y=150)

        # Reading the saved CSV file
        amzColnames = ["Product", "Price", "Rating", "Link"]
        amzData = pd.read_csv("amz.csv", names=amzColnames)

        # Assigning columns from CSV to variables
        amzProducts = amzData.Product.tolist()
        amzPrices = amzData.Price.tolist()
        amzRatings = amzData.Rating.tolist()
        amzLinks = amzData.Link.tolist()

        def onAmzOptionSelected(*args):
            # Getting the product selected and its index in the products array
            selectedProduct = amzOptionVar.get()
            indexOfSelectedProduct = amzProducts.index(selectedProduct)

            # Getting price from the prices list and setting the label text
            priceOfSelectedProduct = str(amzPrices[indexOfSelectedProduct])
            amzPriceLabel.config(text="Price : " + priceOfSelectedProduct)

            # Getting rating from the ratings list and setting the label text
            ratingOfSelectedProduct = amzRatings[indexOfSelectedProduct]
            amzRatingLabel.config(text="Rating : " + ratingOfSelectedProduct)

            # Getting link from the links list
            global amzProductLink
            amzProductLink = str(amzLinks[indexOfSelectedProduct])

        # Variable which points to the selected option in dropdown menu
        amzOptionVar = tk.StringVar(amzFrame)

        # Monitor amzOptionVar for any changes in write mode and call onAmzOptionSelected
        """ trace(mode, callback) """
        amzOptionVar.trace("w", onAmzOptionSelected)

        # Setting the first element of flipProducts as selected option
        amzOptionVar.set(amzProducts[0])

        # Products dropdown menu
        amzOptions = tk.OptionMenu(amzFrame, amzOptionVar, *amzProducts)
        amzOptions.place(x=180, y=97)

        # Rating Label
        amzRatingLabel = tk.Label(
            amzFrame,
            text="Rating : ",
            font=controller.mediumBoldFont,
            bg="black",
            fg="white",
        )
        amzRatingLabel.place(x=300, y=150)

        # Image Processing
        amzImage = Image.open("./assets/amazon-trans.png")
        amzLogo = ImageTk.PhotoImage(amzImage)
        # small = amzLogo.subsample(3, 3)

        # open web page
        new = 1

        def visitAmz():
            webbrowser.open(amzProductLink, new=new)

        # Amazon Visit Label
        amzVisitLabel = tk.Label(
            amzFrame,
            text="Visit Page : ",
            font=controller.mediumBoldFont,
            bg="black",
            fg="white",
        )
        amzVisitLabel.place(x=550, y=70)

        # Visit page button
        visitAmzButton = tk.Button(
            amzFrame,
            font=controller.mediumBoldFont,
            image=amzLogo,
            bg="white",
            command=visitAmz,
        )
        visitAmzButton.place(x=550, y=100)


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="This is the start page", font=controller.largeBoldFont
        )
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(
            self,
            text="Go to Page One",
            command=lambda: controller.show_frame("PageOne"),
        )
        button2 = tk.Button(
            self,
            text="Go to Page Two",
            command=lambda: controller.show_frame("PageTwo"),
        )
        button1.pack()
        button2.pack()


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 1", font=controller.largeBoldFont)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(
            self,
            text="Go to the start page",
            command=lambda: controller.show_frame("StartPage"),
        )
        button.pack()


class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 2", font=controller.largeBoldFont)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(
            self,
            text="Go to the start page",
            command=lambda: controller.show_frame("StartPage"),
        )
        button.pack()


if __name__ == "__main__":
    app = PriceApp()
    app.mainloop()
