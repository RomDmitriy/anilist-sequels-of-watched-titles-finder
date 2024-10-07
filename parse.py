from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from sys import argv

name = argv[1]

transport = AIOHTTPTransport(url="https://graphql.anilist.co/")

client = Client(transport=transport, fetch_schema_from_transport=True)

query = gql(
    """
	query ($name: String!) {
	MediaListCollection(userName: $name, type: ANIME) {
		lists {
		status
		entries {
			media {
				id
				title {
					romaji
					english
					native
				}
				relations {
					edges {
						relationType
						node {
							id
							averageScore
							status
							title {
								romaji
								english
							}
						}
					}
				}
			}
		}
		}
	}
	}
"""
)

result = (client.execute(query, { "name": name }))['MediaListCollection']['lists']

totalList = dict()

for list in result:
	for media in list['entries']:
		totalList[media['media']['id']] = (media['media'])

print('Total:', len(totalList))

completedList = dict()

for list in result:
	for anime in list['entries']:
	    if list['status'] == "COMPLETED":
		    completedList[anime['media']['id']] = anime
		
print('Completed:', len(completedList))
		
sequelEdgeList = dict()

for anime in completedList.values():
	for edge in anime['media']['relations']['edges']:
		if edge['relationType'] == "SEQUEL" and edge['node']['status'] == 'FINISHED' and edge['node']['id'] not in completedList:
			sequelEdgeList[edge['node']['id']] = edge['node']

print('Unwatched sequel (may be dublicates):', len(sequelEdgeList))

sideStoryEdgeList = dict()

for anime in completedList.values():
	for edge in anime['media']['relations']['edges']:
		if edge['relationType'] == "SIDE_STORY" and edge['node']['status'] == 'FINISHED' and edge['node']['id'] not in completedList:
			sideStoryEdgeList[edge['node']['id']] = edge['node']

print('Unwatched side-stories (may be dublicates):', len(sequelEdgeList))

textFile = open(f'output_{name}.txt', 'w')

textFile.write('Sequels:\n')
for anime in sequelEdgeList.values():
	textFile.write(f'\t{anime['title']['english'] or anime['title']['romaji']}\t-\thttps://anilist.co/anime/{anime['id']}/\tScore: {anime['averageScore'] or 'unknown'}%\n')

textFile.write('\nSide-stories:\n')
for anime in sideStoryEdgeList.values():
	textFile.write(f'\t{anime['title']['english'] or anime['title']['romaji']}\t-\thttps://anilist.co/anime/{anime['id']}/\tScore: {anime['averageScore'] or 'unknown'}%\n')