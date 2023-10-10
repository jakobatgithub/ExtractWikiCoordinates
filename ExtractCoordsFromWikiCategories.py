import requests
from bs4 import BeautifulSoup as bs
from xml.dom import minidom
from urllib.parse import urlparse, unquote


def get_human_readable_name(url):
    # Extract the human-readable name from the URL
    parsed_url = urlparse(url)
    path = parsed_url.path
    article_name = path.split('/')[-1]
    decoded_name = unquote(article_name)
    human_readable_name = unquote(decoded_name).replace('_', ' ')
    return human_readable_name


def create_kml_file(coordinates, names, urls, output_file):
    # Create a KML file with coordinates, names, and URLs
    doc = minidom.Document()

    # Create KML root element
    kml = doc.createElement('kml')
    doc.appendChild(kml)

    # Create Document element
    document = doc.createElement('Document')
    kml.appendChild(document)

    # Create Placemark for each coordinate
    for i, coordinate in enumerate(coordinates):
        placemark = doc.createElement('Placemark')
        document.appendChild(placemark)

        # Create name element
        name = doc.createElement('name')
        name_text = doc.createTextNode(names[i])
        name.appendChild(name_text)
        placemark.appendChild(name)

        # Create description element
        description = doc.createElement('description')
        description_text = doc.createTextNode(urls[i])
        description.appendChild(description_text)
        placemark.appendChild(description)

        # Create Point element
        point = doc.createElement('Point')
        placemark.appendChild(point)

        # Create coordinates element
        coordinates_element = doc.createElement('coordinates')
        coordinates_text = doc.createTextNode(f"{coordinate[1]},{coordinate[0]}")  # Swap latitude and longitude order
        coordinates_element.appendChild(coordinates_text)
        point.appendChild(coordinates_element)

    # Write the XML content to the output file
    with open(output_file, 'w') as file:
        file.write(doc.toprettyxml(indent='  '))

    print(f"KML file '{output_file}' created successfully.")


def get_category_urls(categories):
    # Get URLs of Wikipedia pages in specified categories
    base_url = 'https://de.wikipedia.org'
    urls = []

    for category in categories:
        url = f'{base_url}/wiki/Kategorie:{category}'

        response = requests.get(url)
        soup = bs(response.text, 'html.parser')

        # Find all links within the category page
        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if href and href.startswith('/wiki/'):
                if 'Kategorie:' not in href and 'Spezial:' not in href and 'Wikipedia:' not in href and 'Hilfe:' not in href and 'Portal:' not in href:
                    urls.append(f'{base_url}{href}')

    return urls


def get_coordinates(url):
    # Get the latitude and longitude coordinates from a Wikipedia page
    req = requests.get(url).text
    soup = bs(req, 'lxml')
    latitude = soup.find("span", {"class": "latitude"})
    longitude = soup.find("span", {"class": "longitude"})
    if latitude is not None and longitude is not None:
        return (float(latitude.text), float(longitude.text))
    else:
        return None


# Specify the categories you want to extract URLs from
categories = ['Burgruine_in_Thüringen']
# categories = ['Burgruine in Sachsen-Anhalt']
# categories = [
#    'Großsteingrab_im_Landkreis_Ludwigslust-Parchim',
#    'Großsteingrab im Landkreis Mecklenburgische Seenplatte',
#    'Großsteingrab im Landkreis Nordwestmecklenburg',
#    'Großsteingrab im Landkreis Rostock',
#    'Großsteingrab im Landkreis Vorpommern-Greifswald',
#    'Großsteingrab im Landkreis Vorpommern-Rügen'
# ]


# Specify the name of the KML output file
output_filename = 'Koordinaten_Burgruine_Thueringen.kml'
# output_filename = 'Koordinaten_Burgruine_Sachsen-Anhalt.kml'
# output_filename = 'Grosssteingrabkoordinaten_Mecklenburg-Vorpommern.kml'

urls = get_category_urls(categories)

allcoordinates = []
allurls = []
allnames = []
for url in urls:
    coordinates = get_coordinates(url)
    if coordinates is not None:
        name = get_human_readable_name(url)
        print(name)
        allnames.append(name)
        allurls.append(url)
        allcoordinates.append(coordinates)

create_kml_file(allcoordinates, allnames, allurls, output_filename)