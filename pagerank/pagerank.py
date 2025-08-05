import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    complement = 1 - damping_factor

    answer = {p: 0 for p in corpus}

    # We iterate through our model
    links = corpus[page]

    if links:
        # If our key is our page, we get the probabilites for each page based on the damping factor
        prob = damping_factor / len(links)
            
        # Then we assign them our links
        for link in links:
            answer[link] += prob

        # We iterate through answer, adding the probability if the surfer picks any page at random
        distribution = complement / len(answer)
        for key in answer:
            answer[key] += distribution

    else:
        for key in answer:
            answer[key] = 1 / len(answer)

    
    return answer




def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    answer = {p: 0 for p in corpus}
    start_page = random.choice(list(corpus))
    model = transition_model(corpus, start_page, damping_factor)

    for i in range(n):
        next = random.choices(list(model), weights=list(model.values()), k=1)[0]
        answer[next] += 1
        model = transition_model(corpus, next, damping_factor)

    for key in answer:
        answer[key] /= n
    

    return answer



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    threshold = 0.001

    N = len(corpus)
    # We begin by assigning each page to a value of 1/N
    current_ranks = {p: 1/N for p in corpus}

    while True:
        # We have our dictionary set up for when we get the new ranks to compare
        new_ranks = {p: 0 for p in corpus}

        # Variable keeps track if the pageranks have converges
        converged = True

        # Iterate through the pages that we have currently rankes
        for p in current_ranks:
            # Simpe first condition formula
            first_condition = (1 - damping_factor) / N

            # List to represent the incoming links to the current page
            incoming_links = []

            second_condition = 0

            # Iterate through corpus to find all the times our page is in the links
            for page, links in corpus.items():
                # If the page i cannot connect to page p, we assume it connects to all
                if len(links) == 0:
                    second_condition += current_ranks[page] / N

                # If the our page p is found in i's links then we compute normally
                elif p in links:
                    second_condition += current_ranks[page] / len(links)

                # If we had another condition where we tried to look for p in the links and we couldnt find it but it had other links we would do nothing

            # Get the total pagerank by adding them together
            pagerank = first_condition + damping_factor * second_condition

            # Assign it to the new ranks
            new_ranks[p] = pagerank


            # This is in a for loop so we should have all the current ranks done when we exit

        # Now we iterate through the current ranks to compare them to the new ranks
        for page in current_ranks:
            # If our new rank does not fall under the threshold then we set converged to False
            if abs(new_ranks[page] - current_ranks[page]) > threshold:
                converged = False

        # We check if converged is false, if it is we change all the current values to the new ones
        if converged == False:
            for page in current_ranks:
                current_ranks[page] = new_ranks[page]

        # If converged is True, we break out of the loop and return the current converged ranks
        else:
            break


    return current_ranks






        




if __name__ == "__main__":
    main()
