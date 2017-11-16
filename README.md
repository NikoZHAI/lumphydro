# Lumped Hydrological Model: HBV-Web

HBV-Web is an application of lumped hydrological model HBV96 which runs in modern Web browsers. Comparing to many existing versions of HBV model GUIs, HBV-Web provides an intuitive schematisation, interactive figures, and multi-criteria model calibration methods. Implemented in Python, HBV-Web's source code is comprehensible and easy to customize, giving students a better understanding of HBV conceptual model. 

The project was lauched by the IWSG department, Hydroinformatics Chair Group of [UNESCO-IHE](https://www.un-ihe.org/chair-groups/hydroinformatics).

## Overview

<img src="https://github.com/NikoZHAI/lumphydro/tree/plotlyversion/hbvapp/static/img/ScreenShots/main.png" align="center">

### Prerequisites

HBV-Web is based on [Django](https://www.djangoproject.com/) and many other Python libraries. One can install all dependencies by running in a terminal:

```
cd <path_to_your_HBV-Web_root>
pip install -r dependency
```

We presume here that you have already [Python(>=2.7.9)](https://www.python.org/downloads/) installed and you are comfortable with Python package management tools such as [conda](https://conda.io/docs/), [pip](https://pypi.python.org/pypi/pip), etc.

<sub>P.S. All other packages dedicated to front-end functionalities are delivered with HBV-Web or linked to their CDNs.</sub>

### Installing

HBV-Web is developed using [Django](https://www.djangoproject.com/). Once you have successfully installed all required packages in the **`dependency`** file, you are already to go !

<sub>We are currently working on making MS and Linux installers to facilitate installing.</sub>

## Running the application

To run the application, open a terminal, change directory to the **`<HBV-Web_root>`** where exists **`manage.py`** and type:

```
python manage.py runserver
```

Then open the link (**http://127.0.0.1:8000/hbv96/**) in the console with the latest **_Google Chrome_** or **_FireFox_**.

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing and Bug Reporting

Please leave your message in [Issues](https://github.com/NikoZHAI/lumphydro/issues) or contact:

Huanyu **ZHAI** hy.zhai.wyn@gmail.com

[Dr. Juan **Carlos**](https://www.un-ihe.org/juan-carlos-chacon-hurtado)

## Versioning

HBV-Web is still under development. A first realease is comming soon.

## Authors

Huanyu **ZHAI** (Web interface and O-O version of HBV96)

Dr. Juan **Carlos** (Implementation of HBV96, see his [GitHub](https://github.com/j-chacon))

## License

HBV-Web is not yet released or deployed. No license available.

## Acknowledgments

The project was lauched by the IWSG department, Hydroinformatics Chair Group of [UNESCO-IHE](https://www.un-ihe.org/chair-groups/hydroinformatics), under direction of **Prof. Dimitri Solomatine**, **Dr. Juan Carlos Chacon-Hurtado**, and **Dr. Maurizio Mozzaleni**. I deeply appreciate your instructions, advises and help during my internship.

I would also like to thank **Prof. Pierre Brigode** for his advises after I came back to France.

I would never finalize this project without your help !

Equally, I should say "thank you" to all those open-source developers to have provided varies of packages used in this application !


Huanyu ZHAI
