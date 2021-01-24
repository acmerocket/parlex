# parlex

A parler dataset parser written in Python. Intended to work form origin Parler HTML datasets, which can be parsed and analysized using open source Python libraries. 

Also builds standard dataset for loading directly into SQL, document and graph databases, allowing easy data loading from trusted sources. Finally, wraps everything in a few Docker commands and some cloud deployment instructions so everything can be launched to the cloud with existing, open datasets and a ready-to-go DB instance.

### Current Status: work-in-progress

I've got an initial data parser working, that parses a compressed web archive into a series of py dicts that look like:

    {'title': '@TD78 - TD78 - Four years sober from alcohol Mary Jane helped', 'description': 'Four years sober from alcohol Mary Jane helped', 'messageid': '/post/d5cbc10f258b4763873f982dfe6a558e', 'userid': 'https://images.parler.com/68c53f64985e45fb926e810aeecfeacc_256', 'username': '@TD78', 'text': 'Four years sober from alcohol Mary Jane helped', 'impressions': '250', 'link': 'https://www.forbes.com/sites/ajherrington/2021/12/31/marijuana-is-replacing-alcohol-for-nearly-half-of-cannabis-consumers-during-the-pandemic/', 'comments': '0', 'echoes': '0', 'upvotes': '2'}
    {'title': '@BobbyVociferous - BobbyVociferous - Kemp needs to be wiped off the face of the earth...', 'description': 'Kemp needs to be wiped off the face of the earth now', 'messageid': '/post/ae59c03012f94fb7913c3b46fcaa01a3', 'userid': 'https://images.parler.com/fefa5bbc1c4642c6b78f71e590352ae3_256', 'username': '@BobbyVociferous', 'text': 'Kemp needs to be wiped off the face of the earth now', 'impressions': '22', 'link': 'https://www.ajc.com/politics/kemp-condemns-pro-trump-mob-extends-national-guard-order/7WM4YQWAFJB6LFQJ6KD7MAFNJ4/?outputType=wrap', 'comments': '12', 'echoes': '45', 'upvotes': '62'}
    {'title': '@DeepWheat - DeepWheat - ', 'description': 'Parleyed on Parler', 'messageid': '/post/3ace7f35ec264edaae1066214dcc5308', 'userid': 'https://images.parler.com/0f0c82bd48a546bb88fd85e0ce3c8b85_256', 'username': '@CounterGlobalist', 'text': "'*' MUST SEE: '*'Corrupt Hunter Biden Whines to Friend “Every Great Family is Persecuted, Prosecuted in the US” – Poor Biden Crime Syndicate", 'impressions': '1496', 'link': 'https://counterglobalist.news/exclusive-corrupt-hunter-biden-whines-to-friend-every-great-family-is-persecuted-prosecuted-in-the-us-ignoring-biden-family-crimes/', 'comments': '0', 'echoes': '13', 'upvotes': '14'}
    {'title': '@WilburC - WilburC - This was unjustified,Murder!', 'description': 'This was unjustified,Murder!', 'messageid': '/post/c7a954b5201d40d6ba07cf1de68ebafa', 'userid': 'https://images.parler.com/d64c43bfa6a94a1bba2e6c1ee5eb49d7_256', 'username': '@WilburC', 'text': 'This was unjustified,Murder!', 'impressions': '27', 'comments': '12', 'echoes': '27', 'upvotes': '26'}
    {'title': '@GCGI - GCGI - ', 'description': 'Parleyed on Parler', 'messageid': '/post/89eeb62c1f814e6d9c706caccdd059cc', 'userid': 'https://company-media.parler.com/par-default-profile-picture.jpg', 'username': '@BeachMilk', 'text': 'ANTIFA weapons being staged over DC march-area including the obligatory piles of bricks.', 'impressions': '11602', 'comments': '27', 'echoes': '93', 'upvotes': '89'}


## Design

The system will (eventually) consist of:
* extractor: Parse an archive into a well-defined structure.
* loader: Load extracted data into a data system: Export as CSV, SQL, JSON.
* launcher: Launch a cloud/container instance with DB, load scripts and prepared queries.


## Working notes

* researched tooling and existing libraries, found a python parsing lib and a docker impl.
* installing tools and updates for docker tools, to try...


### Grabbing (and other projects)


https://github.com/d0nk/parler-tricks
https://github.com/ArchiveTeam/parler-grab
https://github.com/radicalarchivist/propublica-parler

### Data Processing Tools

https://github.com/d-sanderson/yall-data-hasura

https://github.com/ozywog/parler-data-tools

https://github.com/TheBlindEye/ParlerMetadata

?? https://github.com/sbooeshaghi/parlertrick

### Parsing Notes

HTML -> json/tagged data -> DB (indexed doc db, text search, elastic?)


The metatdata has a lot of good info....

    <meta property="og:title" content="@TD78 - TD78 - Four years sober from alcohol Mary Jane helped" /> -- same as <title>
    <meta property="og:description" content="Four years sober from alcohol Mary Jane helped" /> -- same as <meta desc>
    <meta property="og:url" content="/post/d5cbc10f258b4763873f982dfe6a558e" /> -- Use as message ID (without post), use as PMID
    <meta property="og:image" content="https://images.parler.com/68c53f64985e45fb926e810aeecfeacc_256" /> -- image associated with user, use as PUID (w/o _256)
    
    <span class="author--username">@TD78</span> <-- username
    <span class="impressions--count">250</span> <-- impressions
    
    <div class="card--body">.p text() to get the comment
    
    <div class="mc-article--meta--wrapper"> has links
    
    
Performance metadata:

     <div class="post--actions--row pa--main-row p--flex pf--ac pf--jsb">
            <div class="pa--item--wrapper">
                <img src="/512ae92f/images/icons/comment.svg" alt="Post Comments">
                <span class="pa--item--count">12</span>
            </div>
            <div class="pa--item--wrapper">
                <img src="/512ae92f/images/icons/echo.svg" alt="Post Echoes">
                <span class="pa--item--count">45</span>
            </div>
            <div class="pa--item--wrapper">
                <img src="/512ae92f/images/icons/upvote.svg" alt="Post Upvotes">
                <span class="pa--item--count">62</span>
            </div>
        </div>
    
First pass, pull...
* title
* description
* messageid
* userid
* username
* text

### Parler minilinks?

<span class="mc-article--link">
<a href="https://api.parler.com/l/n1Skh" class="p--flex pf--row pf--ac">https://www.ajc.com/politics/kemp-condemns-pro-trump-mob-extends-national-guard-order/7WM4YQWAFJB6LFQJ6KD7MAFNJ4/?outputType=wrap</a>
</span>

Pull href and link to reproduce link sharing, can count references of the minilink id
    

Other metadata...
    * avatar badge image

