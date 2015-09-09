# Test files

Thanks to alumni of Zepheira's BIBFRAME training <http://zepheira.com/solutions/library/training/> for the following:

George Washington University Libraries (GW_bf_test10.mrx), a single record from which is 700t.mrx

stanford_rda_parens.mrx is from https://foundry.zepheira.com/topics/380

----

lcc-u.mrx - Downloaded from [this LC record](http://catalog2.loc.gov/cgi-bin/Pwebrecon.cgi?v1=1&ti=1,1&Search_Arg=ogbuji&Search_Code=GKEY%5E%2A&CNT=100&type=quick&PID=oYjcPLW0bI3X2GzwJr6jJF3VSR9&SEQ=20141018081442&SID=1) based on an [LC catalogue search for Ogbuji](http://catalog2.loc.gov/cgi-bin/Pwebrecon.cgi?DB=local&Search_Arg=ogbuji&Search_Code=GKEY%5E*&CNT=100&hist=1&type=quick), then converted to MARC/XML as follows:

    yaz-marcdump -i marc -o marcxml -t UTF-8 /tmp/record.mrc > /tmp/record.mrx

TODO: Go back to get non Unicode version when LC.gov is not timing out.

## Other interesting tickets from lcdevnet/marc2bibframe with data attached

 * https://github.com/lcnetdev/marc2bibframe/issues/101
 * [007 field example](https://github.com/lcnetdev/marc2bibframe/issues/91)

----

# Other sources

 * [Free sample MARC data, Koha wiki](http://wiki.koha-community.org/wiki/Free_sample_MARC_data)
 * [Springer download service for CC0 records](http://www.springer.com/?referer=springer.com&SGWID=1-148802-3020-0-0)
 * [MARC .XML Now Available for Naxos Music Library Subscribers](http://naxosmusiclibrary.blogspot.com/2013/10/marc-xml-now-available-for-naxos-music.html)


