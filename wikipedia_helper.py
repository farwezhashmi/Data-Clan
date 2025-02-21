import wikipediaapi

def get_wikipedia_info(landmark_name):
    try:
        # Initialize Wikipedia API
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page = wiki_wiki.page(landmark_name)

        # Check if the page exists
        if page.exists():
            return {
                'summary': page.summary[:1000],  # Limit summary to 1000 characters
                'url': page.fullurl
            }
        else:
            return {
                'error': 'Landmark not found on Wikipedia',
                'summary': '',
                'url': ''
            }

    except Exception as e:
        return {
            'error': f"Error fetching Wikipedia information: {str(e)}",
            'summary': '',
            'url': ''
        }
