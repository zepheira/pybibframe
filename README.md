# pybibframe

Requires Python 3.4 or more recent (also tested with PyPy3.5 v5.7). To install dependencies:

    pip install -r requirements.txt

Then install pybibframe:

    python setup.py install

# Usage

## Converting MARC/XML to RDF or Versa output (command line)

Note: Versa is a model for Web resources and relationships. Think of it as an evolution of Resource Description Framework (RDF) that's at once simpler and more expressive. It's the default internal representation for pybibframe, though regular RDF is an optional output.

    marc2bf records.mrx

Reads MARC/XML from the file records.mrx and outputs a Versa representation of the resulting BIBFRAME records in JSON format. You can send that output to a file as well:

    marc2bf -o resources.versa.json records.mrx

The Versa representation is the primary format for ongoing, pipeline processing.

If you want an RDF/Turtle representation of this file you can do:

    marc2bf -o resources.versa.json --rdfttl resources.ttl records.mrx

If you want an RDF/XML representation of this file you can do:

    marc2bf -o resources.versa.json --rdfxml resources.rdf records.mrx

These two options do build the full RDF model in memory, so they can slow things down quite a bit.

You can get the source MARC/XML from standard input:

    curl http://lccn.loc.gov/2006013175/marcxml | marc2bf

In this case a record is pulled from the Web, in particular Library of Congress Online Catalog / LCCN Permalink. Another example, Das Innere des Glaspalastes in London:

    curl http://lccn.loc.gov/2012659481/marcxml | marc2bf

You can process more than one MARC/XML file at a time by listing them on the command line:

    marc2bf records1.mrx records2.mrx records3.mrx

Or by using wildcards:

    marc2bf records?.mrx

PyBibframe is highly configurable and extensible. You can specify plug-ins from the command line. You need to specify the Python module from which the plugins can be imported and a configuration file specifying how the plugins are to be used. For example, to use the `linkreport` plugin that comes with PyBibframe you can do:

    marc2bf -c config1.json --mod=bibframe.plugin records.mrx

Where the contents of config1.json might be:

	{
	    "plugins": [
                {"id": "http://bibfra.me/tool/pybibframe#labelizer",
                 "lookup": {
                     "http://bibfra.me/vocab/lite/Work": "http://bibfra.me/vocab/lite/title",
                     "http://bibfra.me/vocab/lite/Instance": "http://bibfra.me/vocab/lite/title"
                }
	    ]
	}

Which in this case will add RDFS label statements for Works and Instances to the output.


# Converting MARC/XML to RDF or Versa output (API)

The `bibframe.reader.bfconvert` function can be used as an API to
run the conversion.

	>>> from bibframe.reader import bfconvert
	>>> inputs = open('records.mrx', 'r')
	>>> out = open('resorces.versa.json', 'w')
	>>> bfconvert(inputs=inputs, entbase='http://example.org', out=out)


# Configuration

 * `marcspecials-vocab`: List of vocabulary (base) IRIs to qualify relationships and resource types generated from processing the special MARC fields 006, 007, 008 and the leader.

## Transforms

```
'transforms': {
    'bib': 'http://example.org/vocab/marc-bib-transforms',
}
 ```


# See also

Some open-source tools for working with BIBFRAME (see http://bibframe.org)


Note: very useful to have around yaz-marcdump (which e.g. you can use to conver other MARC formats to MARC/XML)

Download from http://ftp.indexdata.com/pub/yaz/ , unpack then do:

    $ ./configure --prefix=$HOME/.local
    $ make && make install

If you're on a Debian-based Linux you might find useful [these installation notes](https://gist.github.com/uogbuji/7cbc5c62f99951999574)

MarcEdit - http://marcedit.reeset.net/ - can also convert to MARC/XML. Just install, select "MARC Tools" from the menu, choose your input file, specify an output file, and specify the conversion you need to perform, e.g. "MARC21->MARC21XML" for MARC to MARC/XML. Note the availability of the UTF-8 output option too.


## References

 * [MARC 21 Specifications for Record Structure, Character Sets, and Exchange Media: CHARACTER SETS AND ENCODING OPTIONS: Part 4 (Conversion Between Environments)](http://www.loc.gov/marc/specifications/speccharconversion.html)


## Security

  * Possible Python injection attack via configs (even strictly in JSON). Make sure you check for tainting.

# Acknowledgements

pybibframe developement, led by Zepheira, has been supported in part by the Library of Congress, BIBFLOW (an IMLS project of the UC Davis library), and thanks to contributions and refinements to the default transformation recipes made by librarians participating in Zepheira's Linked Data and BIBFRAME Practical Practitioner Training program

* [Bibframe](http://bibframe.org/)
* [Zepheira](http://zepheira.com/)
* [Library of Congress](http://loc.gov/)
* [BIBFLOW](http://www.lib.ucdavis.edu/bibflow/)
* [Zepheira Linked Data and BIBFRAME Practical Practitioner Training](http://zepheira.com/solutions/library/training/)
