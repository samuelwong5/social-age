import csv
import models

with open('fb_twitter_lookup.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    try:
        while True:
            curr = reader.next()
            next = reader.next()
            while (curr[0] != next[0]):
                curr = next
                next = reader.next()
            if curr[3] == 'twitter':
                tw_id = curr[2]
                tw_handle = curr[4]
                fb_id = next[2]
                fb_handle = next[4]
            else:
                fb_id = curr[2]
                fb_handle = curr[4]
                tw_id = next[2]
                tw_handle = next[4]
            id = curr[0]
            name = curr[6]
            models.Page.objects.create(id=id,
                                       name=name,
                                       fb_id=fb_id,
                                       fb_handle=fb_handle,
                                       tw_id=tw_id,
                                       tw_handle=tw_handle,
                                       probs='0,0,0,0,0,0,0,0,0,0')
    except:
        pass # No more rows
    
