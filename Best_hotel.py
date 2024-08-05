import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Combobox
from tkcalendar import Calendar
import tkinter.messagebox as mbox
from PIL import Image, ImageTk

def valid_checkin_checkout_dates(checkinout):
    try:
        checkinout = datetime.strptime(checkinout, "%Y/%m/%d")
        if checkinout < datetime.today():
            tk.messagebox.showwarning("Invalid Date", "You entered a past date, please enter a valid date.")
            return False
        return True
    except ValueError:
        tk.messagebox.showwarning("Invalid Format", "You entered a wrong date format.")
        return False

def hotel_scraping(city_combo,checkin_cal,checkout_cal,number_of_adults_entry,number_of_children_entry,number_of_rooms_entry,currency_radio,sort_option_radio):
    Cities = {
        'Tokyo':-246227,
        'Barcelona':-372490,
        'Paris':-1456928,
        'Seul':-716583,
        'Madrid':-390625,
        'Amsterdam':-2140479,
        'Berlin':-1746443,
        'Roma':2282,
        'Londra':-2601889,
        'Singapur':-73635
    }

    while True:
        city = city_combo.get()
        if city in Cities:
            break

    checkin = checkin_cal.get()
    checkout = checkout_cal.get()
    if valid_checkin_checkout_dates(checkin) and valid_checkin_checkout_dates(checkout) and checkout>checkin:
        number_of_adults = number_of_adults_entry.get()
        number_of_children = number_of_children_entry.get()
        number_of_rooms = number_of_rooms_entry.get()
        a = Cities[city] #to add in url

        url = f'https://www.booking.com/searchresults.html?ss={city}&ssne={city}&ssne_untouched={city}&efdco=1&label=gen173nr-1FCAEoggI46AdIM1gEaOQBiAEBmAExuAEHyAEP2AEB6AEBAECiAIBqAIDuAKo8sKxBsACAdICJGZlZWVmNGJjLWI2OGEtNGM0OS05ODk0LTM2ZGQ4YzkxYzY0MNgCBeACAQ&aid=304142&lang=en-us&sb=1&src_elem=sb&src=index&dest_id={a}&dest_type={city}&checkin={checkin}&checkout={checkout}&group_adults={number_of_adults}&no_rooms={number_of_rooms}&group_children={number_of_children}'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'}

        currency = currency_radio.get()
        sort_option = sort_option_radio.get()

        #print("Searching URL:", url)

        response = requests.get(url,headers=headers)
        #requests taking the website url and store as a variable
        soup = BeautifulSoup(response.text,'html.parser')
        #BeatifulSoup parse the html format and store it as variable too

        hotels = soup.findAll('div', {'data-testid': 'property-card'})[:10]
        hotels_data = []
        for hotel in hotels:
            name = hotel.find('div', {'data-testid': 'title'})
            hotel_name = name.text.strip()

            address = hotel.find('span', {'data-testid': 'address'})
            hotel_address = address.text.strip()

            distance = hotel.find('span', {'data-testid': 'distance'})
            hotel_distance = distance.text.strip()

            rating = hotel.find('a', {'data-testid': 'secondary-review-score-link'})
            if rating is not None:
                hotel_rating = rating.text.strip()
            else:
                hotel_rating = "NOT GIVEN"

            price = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
            hotel_price = price.text.strip()[3:].replace('TL','').strip() #for omitting the currency symbol -> TL or €
            hotel_price = hotel_price.replace(',','') #for omitting comma to convert float
            hotel_price_float = float(hotel_price)
            if currency == "€":
                hotel_price_float = hotel_price_float/30
            else :
                hotel_price_float = hotel_price_float

            hotels_data.append({
                'Hotel Name: ': hotel_name,
                'Hotel Address: ': hotel_address,
                'Distance To City Center: ': hotel_distance,
                'Hotel Rating: ': hotel_rating,
                'Hotel Price: ': hotel_price_float
            })

        hotels = pd.DataFrame(hotels_data)

        if sort_option == 'mtl':
            hotels_sorted = hotels.sort_values(by='Hotel Price: ', ascending=False)
        else:
            hotels_sorted = hotels.sort_values(by='Hotel Price: ', ascending=True)

        hotels_sorted.to_csv('test_hotels.csv', header=True, index=False)
        hotels.head()

        listboxhotels.config(state='normal')
        listboxhotels.delete(0, tk.END)
        for index,hotel in hotels_sorted.head(5).iterrows():
            listboxhotels.insert(tk.END, f"Hotel Name: {hotel['Hotel Name: ']}\n")
            listboxhotels.insert(tk.END, f"Hotel Address: {hotel['Hotel Address: ']}\n")
            listboxhotels.insert(tk.END, f"Distance To City Center: {hotel['Distance To City Center: ']}\n")
            listboxhotels.insert(tk.END, f"Hotel Rating: {hotel['Hotel Rating: ']}\n")
            listboxhotels.insert(tk.END, f"Hotel Price: {hotel['Hotel Price: ']}\n")
            listboxhotels.insert(tk.END, "\n")
    else:
        print("WRONG")


window =tk.Tk()
window.title('BEST HOTEL')
window.state('zoomed')

top_frame = tk.LabelFrame(window,
                          width=1920,
                          height=145,
                          bg='steel blue').place(x=0, y=0)

right_frame = tk.LabelFrame(window,
                            width=1375,
                            height=875,
                            bg='light sky blue').place(x=545, y=145)

left_top_frame = tk.LabelFrame(window,
                               width=545,
                               height=145,
                               bg='grey').place(x=0, y=145)

left_bottom_frame = tk.LabelFrame(window,
                                  width=545,
                                  height=730,
                                  bg='dark grey').place(x=0,y=290)

title_label = tk.Label(top_frame,
                       text='BEST HOTEL',
                       font='Arial 50 bold',
                       bg='steel blue').place(x=715,y=35)

currency_gui = tk.StringVar(value='TL')

currency_label = tk.Label(left_top_frame,
                          text='Price Currency = ',
                          font='TimesNewRoman 15 bold',
                          fg='light grey',
                          bg='grey')
currency_label.place(x=60,y=170)

currency_radio_euro = tk.Radiobutton(left_top_frame,
                                text='EURO',
                                activebackground='grey',
                                value='€',
                                variable=currency_gui)
currency_radio_euro.place(x=260,y=171)

currency_radio_tl = tk.Radiobutton(left_top_frame,
                                text='TL',
                                activebackground='grey',
                                value='TL',
                                variable=currency_gui)
currency_radio_tl.place(x=350,y=171)

sort_option_gui = tk.StringVar(value='mtl')


sort_option_label = tk.Label(left_top_frame,
                             text='Sort Option For Price = ',
                             font='TimesNewRoman 15 bold',
                             fg='light grey',
                             bg='grey')
sort_option_label.place(x=60, y=232)

sort_option_radio_mtl = tk.Radiobutton(left_top_frame,
                                text='DSC',
                                activebackground='grey',
                                value='mtl',
                                variable=sort_option_gui)
sort_option_radio_mtl.place(x=320,y=233)

sort_option_radio_ltm = tk.Radiobutton(left_top_frame,
                                text='ASC',
                                activebackground='grey',
                                value='ltm',
                                variable=sort_option_gui)
sort_option_radio_ltm.place(x=400,y=233)

city_combo=tk.StringVar()

city_label = tk.Label(left_bottom_frame,
                      text='City = ',
                      font='TimesNewRoman 15 bold',
                      fg='grey',
                      bg='dark grey')
city_label.place(x=60,y=320)

city_combo=Combobox(left_bottom_frame,
                    values=("Select a City","Tokyo","Barcelona","Paris","Seul","Madrid","Amsterdam","Berlin","Roma","Londra","Singapur"),
                    state='readonly')
city_combo.place(x=150,y=323)

checkin_date_gui=tk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))
checkout_date_gui=tk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))

checkin_date_label=tk.Label(left_bottom_frame,
                            text='Checkin Date = ',
                            font='TimesNewRoman 15 bold',
                            fg='grey',
                            bg='dark grey')
checkin_date_label.place(x=60,y=370)

checkin_date_calendar = Calendar(left_bottom_frame,
                                 selectmode="day",
                                 date_pattern="yyyy/MM/dd",
                                 textvariable=checkin_date_gui)
checkin_date_calendar.place(x=230,y=370)

checkout_date_label=tk.Label(left_bottom_frame,
                             text='Checkout Date = ',
                             font='TimesNewRoman 15 bold',
                             fg='grey',
                             bg='dark grey')
checkout_date_label.place(x=60,y=580)

checkout_date_calendar = Calendar(left_bottom_frame,
                                 selectmode="day",
                                 date_pattern="yyyy/MM/dd",
                                 textvariable=checkout_date_gui)
checkout_date_calendar.place(x=230,y=580)

noa_entry= tk.IntVar()

number_of_adults_label=tk.Label(left_bottom_frame,
                             text='Number Of Adults = ',
                             font='TimesNewRoman 15 bold',
                             fg='grey',
                             bg='dark grey')
number_of_adults_label.place(x=60,y=790)

number_of_adults_entry=tk.Entry(left_bottom_frame,
                                width=30,
                                textvariable=noa_entry)
number_of_adults_entry.place(x=280,y=795)

noc_entry= tk.IntVar()

number_of_children_label=tk.Label(left_bottom_frame,
                             text='Number Of Children = ',
                             font='TimesNewRoman 15 bold',
                             fg='grey',
                             bg='dark grey')
number_of_children_label.place(x=60,y=840)

number_of_children_entry=tk.Entry(left_bottom_frame,
                                  width=30,
                                  textvariable=noc_entry)
number_of_children_entry.place(x=280,y=845)

nor_entry= tk.IntVar()

number_of_rooms_label=tk.Label(left_bottom_frame,
                             text='Number Of Rooms = ',
                             font='TimesNewRoman 15 bold',
                             fg='grey',
                             bg='dark grey')
number_of_rooms_label.place(x=60,y=890)

number_of_rooms_entry=tk.Entry(left_bottom_frame,
                               width=30,
                               textvariable=nor_entry)
number_of_rooms_entry.place(x=280,y=895)

def show_hotels():

    if not city_combo.get() or city_combo.get() == "Select a City":
        mbox.showerror("Error", "Please select a city.")
        return

    if not checkin_date_gui.get() or not checkout_date_gui.get():
        mbox.showerror("Error", "Please select check-in and check-out dates.")
        return

    if not noa_entry.get():
        mbox.showerror("Error", "Please enter the number of adults.")
        return

    if not noc_entry.get():
        mbox.showerror("Error", "Please enter the number of children.")
        return

    if not nor_entry.get():
        mbox.showerror("Error", "Please enter the number of rooms.")
        return

    listboxhotels.config(state='normal')
    listboxhotels.delete(0, tk.END)

    try:
        hotel_scraping(city_combo, checkin_date_gui, checkout_date_gui, noa_entry, noc_entry, nor_entry, currency_gui, sort_option_gui)
        myphoto= Image.open("C:\\Users\\Casper\\PycharmProjects\\BestHotelHK\\WhatsApp Görsel 2024-05-20 saat 01.30.54_856d1c7f.jpg")
        new_width=600
        new_height=750
        resized_image = myphoto.resize((new_width, new_height),Image.LANCZOS)

        tk_image=ImageTk.PhotoImage(resized_image)
        label1=tk.Label(right_frame,image=tk_image)
        label1.image=tk_image
        label1.place(x=1250,y=200)

    except Exception as e:
        mbox.showerror("Error", f"An error occurred: {e}")

listboxhotels= tk.Listbox(right_frame,
                          width=116,
                          height=31,
                          font='TimesNewRoman 15 bold')
listboxhotels.place(x=595,y=195)


search_button= tk.Button(left_bottom_frame,
                         text='Search Hotels',
                         command=show_hotels)
search_button.place(x=200,y=950)

window.mainloop()