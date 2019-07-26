import pandas as pd
import networkx as nx
from FeatureExtraction import FeatureExtraction
from SocialNetworkAnalysis import SocialNetworkAnalysis


def main():
    # feature_extraction = FeatureExtraction()
    # alexa_df = pd.read_csv('resources/top-1m.csv', names=['rank', 'domain'])
    # domain_list = alexa_df['domain'][:100]
    # df = feature_extraction.extract(domain_list, label=0)
    # df.to_csv('top_benign.csv', index=False)
    
    df = pd.read_csv('top_benign.csv')
    domain_list = df['domain'][:500]

    sna = SocialNetworkAnalysis()
    df.apply(sna.append_row_to_graph, axis=1)

    

    # for domain in domain_list:
    #     print(domain, sna.G.nodes[domain]['current'])

    print('------------------------------------------------------------------')

    sna.stable_graph()
    for domain in domain_list:
        print(domain, sna.G.nodes[domain]['current'])

    print (len(sna.G))

if __name__ == "__main__":
    main()