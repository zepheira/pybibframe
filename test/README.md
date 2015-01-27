# Running & maintaining the test suite

Run as follows:

	py.test test/test_marc_basics.py 
    
If you update code in a way that affects output, you can update the expected output
(once you've verified that the new output is more correct, of course)
as in the following example.

    cd test/resource
    marc2bf gunslinger.mrx --canonical -o gunslinger.versa
    marc2bf egyptskulls.mrx --canonical -o egyptskulls.versa
    marc2bf joycebcat-140613.mrx --canonical -o joycebcat-140613.versa 
    marc2bf kford-holdings1.mrx --canonical -o kford-holdings1.versa 
    marc2bf timathom-140716.mrx --canonical -o timathom-140716.versa 
    cd -

