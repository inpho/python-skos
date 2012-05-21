# Python SKOS

[![Build Status](https://secure.travis-ci.org/homme/python-skos.png)](http://travis-ci.org/homme/python-skos)

## Overview

This package provides a basic implementation of *some* of the core
elements of the SKOS object model, as well as an API for loading SKOS
XML resources.  See the
[SKOS Primer](http://www.w3.org/TR/skos-primer) for an introduction to
SKOS.

The object model builds on [SQLAlchemy](http://sqlalchemy.org) to
provide persistence and querying of the object model from within a SQL
database.

## Usage

Firstly, the package supports Python's
[logging module](http://docs.python.org/library/logging.html) which
can provide useful feedback about various module actions so let's
activate it:

    >>> import logging
    >>> logging.basicConfig(level=logging.INFO)
    
The package reads graphs generated by the `rdflib` library so let's
parse a (rather contrived) SKOS XML file into a graph:

    >>> import rdflib
    >>> xml = """<?xml version="1.0"?>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:skos="http://www.w3.org/2004/02/skos/core#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:owlxml="http://www.w3.org/2006/12/owl2-xml#">
      <skos:Concept rdf:about="http://my.fake.domain/test1">
        <skos:prefLabel>Acoustic backscatter in the water column</skos:prefLabel>
        <skos:definition>Includes all parameters covering the strength of acoustic signal return, including absolute measurements of returning signal strength as well as parameters expressed as backscatter (the proportion of transmitted signal returned)</skos:definition>
        <owlxml:sameAs rdf:resource="http://vocab.nerc.ac.uk/collection/L19/current/005/"/>
        <skos:broader rdf:resource="http://vocab.nerc.ac.uk/collection/P05/current/014/"/>
        <skos:narrower rdf:resource="http://vocab.nerc.ac.uk/collection/P01/current/ACBSADCP/"/>
        <skos:related rdf:resource="http://my.fake.domain/test2"/>
      </skos:Concept>
      <skos:Collection rdf:about="http://my.fake.domain/collection">
        <dc:title>Test Collection</dc:title>
        <dc:description>A collection of concepts used as a test</dc:description>
        <skos:member rdf:resource="http://my.fake.domain/test1"/>
        <skos:member>
          <skos:Concept rdf:about="http://my.fake.domain/test2">
            <skos:prefLabel>Another test concept</skos:prefLabel>
            <skos:definition>Just another concept</skos:definition>
            <skos:related rdf:resource="http://my.fake.domain/test1"/>
          </skos:Concept>
        </skos:member>
      </skos:Collection>
    </rdf:RDF>"""
    >>> graph = rdflib.Graph()
    >>> graph.parse(data=xml, format="application/rdf+xml")

Now we can can use the `skos.RDFLoader` object to access the SKOS data
as Python objects:

    >>> import skos
    >>> loader = skos.RDFLoader(graph)
    
This implements a mapping interface:

    >>> loader.keys()
    ['http://my.fake.domain/test1',
     'http://my.fake.domain/test2',
     'http://my.fake.domain/collection']
    >>> loader.values()
    [<Concept('http://my.fake.domain/test1')>,
     <Concept('http://my.fake.domain/test2')>,
     <Collection('http://my.fake.domain/collection')>]
    >>> len(loader)
    3
    >>> concept = loader['http://my.fake.domain/test1']
    >>> concept
    <Concept('http://my.fake.domain/test1')>
    
As well as some convenience methods returning mappings of specific
types:

    >>> loader.getConcepts()
    {'http://my.fake.domain/test1': <Concept('http://my.fake.domain/test1')>,
     'http://my.fake.domain/test2': <Concept('http://my.fake.domain/test2')>}
    >>> loader.getCollections()
    {'http://my.fake.domain/collection': <Collection('http://my.fake.domain/collection')>}
    >>> loader.getConceptSchemes() # we haven't got any `ConceptScheme`s
    {}    

The `RDFLoader` constructor also takes a `max_depth` parameter which
defaults to `0`.  This parameter determines the depth to which RDF
resources are resolved i.e. it is used to limit the depth to which
links are recursively followed.  E.g. the following will allow one
level of external resources to be parsed and resolved:

    >>> loader = skos.RDFLoader(graph, max_depth=1) # you need to be online for this!
    INFO:skos:parsing http://vocab.nerc.ac.uk/collection/L19/current/005/
    INFO:skos:parsing http://vocab.nerc.ac.uk/collection/P05/current/014/
    INFO:skos:parsing http://vocab.nerc.ac.uk/collection/P01/current/ACBSADCP/

If you want to resolve an entire (and potentially very large!) graph
then use `max_depth=float('inf')`.

Another constructor parameter is the boolean flag `flat`. This can
also be toggled post-instantiation using the `RDFLoader.flat`
property.  When set to `False` (the default) only SKOS objects present
in the inital graph are directly referenced by the loader: objects
created indirectly by parsing other resources will only be referenced
by the top level objects:

    >>> loader.keys() # lists 3 objects
    ['http://my.fake.domain/test1',
     'http://my.fake.domain/test2',
     'http://my.fake.domain/collection']
    >>> concept = loader['http://my.fake.domain/test1']
    >>> concept.synonyms # other objects are still correctly referenced by the object model
    {'http://vocab.nerc.ac.uk/collection/L19/current/005/': <Concept('http://vocab.nerc.ac.uk/collection/L19/current/005/')>}
    >>> 'http://vocab.nerc.ac.uk/collection/L19/current/005/' in loader # but are not referenced directly
    False
    >>> loader.flat = True # flatten the structure so *all* objects are directly referenced
    >>> loader.keys() # lists all 6 objects
    ['http://vocab.nerc.ac.uk/collection/P05/current/014/',
     'http://vocab.nerc.ac.uk/collection/L19/current/005/',
     'http://my.fake.domain/collection',
     'http://my.fake.domain/test1',
     'http://my.fake.domain/test2',
     'http://vocab.nerc.ac.uk/collection/P01/current/ACBSADCP/']
    >>> 'http://vocab.nerc.ac.uk/collection/L19/current/005/' in loader
    True

The `Concept.synonyms` demonstrated above shows the container (an
instance of `skos.Concepts`) into which `skos::exactMatch` and
`owlxml::sameAs` references are placed. The `skos.Concepts` container
class is a mapping that is mutable via the `set`-like `add` and
`discard` methods, as well responding to `del` on keys:

    >>> synonym = skos.Concept('test3', 'a synonym for test1', 'a definition')
    >>> concept.synonyms.add(synonym)
    >>> concept.synonyms
    {'http://vocab.nerc.ac.uk/collection/L19/current/005/': <Concept('http://vocab.nerc.ac.uk/collection/L19/current/005/')>,
     'test3': <Concept('test3')>}
    >>> del concept.synonyms['test3'] # or...
    >>> concept.synonyms.discard(synonym)

Similar to `Concept.synonyms` `Concept.broader`, `Concept.narrower`
and `Concept.related` are all instances of `skos.Concepts`:

    >>> assert concept in concept.broader['http://vocab.nerc.ac.uk/collection/P05/current/014/'].narrower

`Concept` instances also provide easy access to the other SKOS data:

    >>> concept.uri
    'http://my.fake.domain/test1'
    >>> concept.prefLabel
    'Acoustic backscatter in the water column'
    >>> concept.definition
    'Includes all parameters covering the strength of acoustic signal return, including absolute measurements of returning signal strength as well as parameters expressed as backscatter (the proportion of transmitted signal returned)'

Access to the `ConceptScheme` and `Collection` objects to which a
concept belongs is also available via the `Concept.schemes` and
`Concept.collections` properties respectively:

    >>> concept.collections
    {'http://my.fake.domain/collection': <Collection('http://my.fake.domain/collection')>}
    >>> collection = concept.collections['http://my.fake.domain/collection']
    >>> assert concept in collection.members
    
As well as the `Collection.members` property, `Collection` instances
provide access to the other SKOS data:

    >>> collection.uri
    'http://my.fake.domain/collection'
    >>> collection.title
    collection.title
    >>> collection.description
    'A collection of concepts used as a test'

`Collection.members` is a `skos.Concepts` instance, so new members can
added and removed using the `skos.Concepts` interface:

    >>> collection.members.add(synonym)
    >>> del collection.members['test3']

### Integrating with SQLAlchemy

`python-skos` has been designed to be integrated with the SQLAlchemy
ORM when required.  This provides scalable data persistence and
querying capabilities.  The following example uses an in-memory SQLite
database to provide a taste of what is possible. Explore the
[SQLAlchemy ORM documentation](http://docs.sqlalchemy.org/en/latest/)
to build on this, using alternative databases and querying
techniques...

    >>> from sqlalchemy import create_engine
    >>> engine = create_engine('sqlite:///:memory:') # the in-memory database
    >>> from sqlalchemy.orm import sessionmaker
    >>> Session = sessionmaker(bind=engine)
    >>> session1 = Session() # get a session handle on the database
    >>> skos.Base.metadata.create_all(session1.connection()) # create the required database schema
    >>> session1.add_all(loader.values()) # add all the skos objects to the database
    >>> session1.commit() # commit these changes

    >>> session2 = Session() # a new database session, created somewhere else ;)
    >>> session2.query(skos.Collection).first() # obtain our one and only collection
    <Collection('http://my.fake.domain/collection')>
    >>> # get all concepts that have the string 'water' in them:
    >>> session2.query(skos.Concept).filter(skos.Concept.prefLabel.ilike('%water%')).all()
    [<Concept('http://my.fake.domain/test1')>,
     <Concept('http://vocab.nerc.ac.uk/collection/P01/current/ACBSADCP/')>]

## Requirements

- [Python](http://www.python.org) == 2.{6,7}
- [SQLAlchemy](http://www.sqlalchemy.org) SQLAlchemy >= 0.7.5
- [RDFLib](http://pypi.python.org/pypi/rdflib) >= 2.4.2
- [unittest2](http://pypi.python.org/pypi/unittest2) if running the tests with Python < 2.7

## Download

Current and previous versions of the software are available at
<http://github.com/geo-data/python-skos/tags> and
<http://pypi.python.org/pypi/python-skos>.

## Installation

Download and unpack the source, then run the following from the root
distribution directory:

    python setup.py install

It is recommended that you also run:

    python setup.py test

This exercises the comprehensive package test suite.

## Limitations

- Only part of the more recent SKOS core object model is
  supported. Extending the code to support more of the SKOS
  specification should not be difficult, however.

- This is a new and immature package: please treat it as beta quality
  software and report any bugs in the github issue tracker. Having
  said that it sees production use in the
  [MEDIN Portal](https://github.com/geo-data/medin-portal) and
  [MEDIN metadata tool](https://github.com/geo-data/medin-rdbms-tool)
  software.
