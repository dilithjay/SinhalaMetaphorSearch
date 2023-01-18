# SinhalaMetaphorSearch
A search application for metaphors found in Sinhala songs that were released during the past decade.

### Create index with mapping file
```
curl -X PUT "localhost:9200/sinhala-song-metaphors?pretty" -H "Content-Type: application/json" -u elastic:elastic -d @jsons/mapping_file.json
```


### Load data
```
curl -X PUT "localhost:9200/sinhala-song-metaphors/_bulk?pretty" -H "Content-Type: application/json" -u elastic:elastic --data-binary @jsons/data.json
```


