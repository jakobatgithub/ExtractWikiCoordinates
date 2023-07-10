import requests
from bs4 import BeautifulSoup as bs
from xml.dom import minidom
from urllib.parse import urlparse, unquote


def get_human_readable_name(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    article_name = path.split('/')[-1]
    decoded_name = unquote(article_name)
    human_readable_name = unquote(decoded_name).replace('_', ' ')
    return human_readable_name


def get_article_name(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    article_name = path.split('/')[-1]
    return article_name


def get_category_urls(category):
    base_url = 'https://de.wikipedia.org'
    url = f'{base_url}/wiki/Kategorie:{category}'

    response = requests.get(url)
    soup = bs(response.text, 'html.parser')

    urls = []

    # Find all links within the category page
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href and href.startswith('/wiki/'):
            if 'Kategorie:' not in href:
                if 'Spezial:' not in href:
                    if 'Wikipedia:' not in href:
                        if 'Hilfe:' not in href:
                            if 'Portal:' not in href:
                                urls.append(f'{base_url}{href}')

    return urls


def get_coordinates(url):
    req = requests.get(url).text
    soup = bs(req, 'lxml')
    latitude = soup.find("span", {"class": "latitude"})
    longitude = soup.find("span", {"class": "longitude"})
    if latitude is not None:
        if longitude is not None:
            return (float(latitude.text), float(longitude.text))
    else:
        return None


def create_kml_file(coordinates, names, urls, output_file):
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



# Specify the categories you want to extract URLs from
categories = [
    'Großsteingrab_im_Landkreis_Ludwigslust-Parchim', 
    'Großsteingrab im Landkreis Mecklenburgische Seenplatte', 
    'Großsteingrab im Landkreis Nordwestmecklenburg',
    'Großsteingrab im Landkreis Rostock',
    'Großsteingrab im Landkreis Vorpommern-Greifswald',
    'Großsteingrab im Landkreis Vorpommern-Rügen']

# Specify the name of the kml output file
output_filename = 'Grosssteingrabkoordinaten_Mecklenburg-Vorpommern.kml'

urls = []
for category in categories:
    urls.extend(get_category_urls(category))

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