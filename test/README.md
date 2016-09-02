# Running & maintaining the test suite

Run as follows:

	py.test test

If you update code in a way that affects output, you can update the expected output
(once you've verified that the new output is more correct, of course)
The following example shows how to do so for test_use_cases.py:

    cd test/resource
    marc2bf gunslinger.mrx --canonical -o gunslinger.versa
    marc2bf egyptskulls.mrx --canonical -o egyptskulls.versa
    marc2bf joycebcat-140613.mrx --canonical -o joycebcat-140613.versa
    marc2bf kford-holdings1.mrx --canonical -o kford-holdings1.versa
    marc2bf timathom-140716.mrx --canonical -o timathom-140716.versa
    marc2bf zweig.mrx --canonical -o zweig.versa
    marc2bf zweig-tiny.mrx --canonical -o zweig-tiny.versa
    cd -

For test_marc_snippets.py use the following recipe to regenerate the test case expected outputs:

	python -i test/test_marc_snippets1.py #Ignore the SystemExit
	python -i test/test_marc_snippets2.py #Ignore the SystemExit

Then:

{{{
all_snippets = sorted([ sym for sym in globals() if sym.startswith('SNIPPET') ])
all_config = sorted([ sym for sym in globals() if sym.startswith('CONFIG') ])
all_expected = sorted([ sym for sym in globals() if sym.startswith('EXPECTED') ])

for s, c, e in zip(all_snippets, all_config, all_expected):
    sobj, cobj, eobj = globals()[s], globals()[c], globals()[e]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)
    m = memory.connection()
    instream = BytesIO(sobj.encode('utf-8'))
    outstream = StringIO()
    bfconvert(instream, model=m, out=outstream, config=cobj, canonical=True, loop=loop)
    print('EXPECTED from {0}:'.format(s))
    print(outstream.getvalue()) #This output becomes the EXPECTED stanza
}}}

Then copy the corresponding EXPECTED stanzas to the right place in the test file.

# Expanding the test suite

* ["structural marc problems you may encounter"](https://bibwild.wordpress.com/2010/02/02/structural-marc-problems-you-may-encounter/) is a good chamber of horrors. We should check that we handle the given cases gracefully.
