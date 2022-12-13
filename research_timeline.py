# Ask if the user wants to create new timeline or add to a previously created one
print('The following program allows you to input research article citations and receive a research timeline organized by author and date. You will be able to choose which format you would like for your output: a CSV file, timeline, or both. The output will be saved on your computer in the same folder as this program.')

# Ask them to input database file name, establish while loop to be able to run through program with both options (new/old)
while True :
    # Begin "new" option - create three file names, one each for the resulting database, CSV, and/or timeline
    new_old = input('\nWould you like to create a new timeline, or add to a previous timeline created with this program? Please enter either "new" or "old." ')
    if new_old == 'new' : 
        project_name = input('\nPlease name your timeline files. Enter one name to be used for all files created by this program. If the name contains multiple words, connect them with "_" such as "project_name" ')
        db_name = project_name + '.db'
        csv_name = project_name + '.csv'
        timeline_name = project_name + '.pdf'

    # Create database and table
        import sqlite3
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.executescript('''
            DROP TABLE IF EXISTS Articles;

            CREATE TABLE Articles (
                id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                Author TEXT,
                Date   TEXT,
                Title  TEXT UNIQUE,
                DOI    TEXT UNIQUE
            )
            ''')
        conn.close()

    # Print file input instructions for user
        print('\nYou will now be repeatedly prompted to enter a file name or "Done." The file must be a ".txt" text file of an article citation with one or more authors. Once you are finished inputting research articles, enter "Done."')

    # Establish loop so user can input many files
        while True:

    # Prompt user for file
            fname = input('\nEnter file name or Done: ')
            if fname == 'Done' :
                break
            try :
                fhandle = open(fname)
            except :
                print('\nFile cannot be opened')
                continue

        # Parse and extract article title
            lines = fhandle.readlines() 
            title = lines[1].rstrip()

        # Parse and extract article date
            import re
            numlist = list()
            for line in lines:
                num = re.findall('\d{4}' , line)
                if num not in numlist : numlist.append(num)
            numlist = list(filter(None, numlist))
            select_date = numlist[0]
            convert_date = str(select_date)
            date = convert_date[2 : 6]

        # Parse and extract article author or primary author, format as Last, First
            authorlist = list()
            authorline = lines[0]
            persons = authorline.split(',')
            for person in persons:
                if person not in authorlist : authorlist.append(person)
            a = authorlist[0]
            a_split = a.split(' ')
            a_split.reverse()
            author = a_split[0] + ', ' + a_split[-1:][0]
    
        # Parse and extract article DOI
            for line in lines:
                if line.startswith('https://d'):
                    doi = line

        # Add the extracted metadata to the database table
            conn = sqlite3.connect(db_name)
            cur = conn.cursor()
            cur.execute('''INSERT INTO Articles 
                    (Author, Date, Title, DOI) VALUES (?, ?, ?, ?)''',
                    (author, date, title, doi) )
            conn.commit()
            conn.close()

            # Continue loop so user can input more articles
            continue

    # Once user enters "Done" the loop breaks - now user is asked to choose output format(s)
        print('\nPlease select the format(s) in which you would like your output.')

        while True:

            output_format = input('\nEnter "CSV" or "Timeline" or "Both": ')
            if output_format == 'CSV' or output_format =='Timeline' or output_format == 'Both' :
                print('\nYou have selected' , output_format)

            else : print('\nPlease enter valid output format.')

        # If user selects CSV, generate and save a CSV file of the table ordered by author and date
            if output_format == 'CSV' :
                import pandas as pd
                from glob import glob; from os.path import expanduser

                conn = sqlite3.connect(db_name)
                cur = conn.cursor()
                article_metadata = pd.read_sql('SELECT * FROM Articles ORDER BY Author, Date' ,conn)
                # Save the CSV file on the user computer using the file name they input at the beginning (csv_name)
                article_metadata.to_csv(csv_name, index=False)
                conn.close()
                quit()

        # If user selects timeline, generate horizontal research timeline
            elif output_format == 'Timeline' :
                import matplotlib.pyplot as plt
                import numpy as np

                conn = sqlite3.connect(db_name)
                cur = conn.cursor()

                # Pull dates from database, format them as strings with date on one line and author on the next, put in new strings list of chronologically ordered dates
                cur.execute('SELECT Date , Author FROM Articles')
                dates = cur.fetchall()
                date_strings = list()
                for da in dates :
                    datestr = ''.join(da)
                    datestr_format = datestr[:4] + '\n' + datestr[4:]
                    if datestr_format not in date_strings : date_strings.append(datestr_format)
                    dates_ordered = sorted(date_strings)

                conn.commit()
                conn.close()

                # Define the timeline labels as the chronological dates
                labels = dates_ordered

                # Use horizonal line and scatter plot functions to set up timeline and points
                fig, ax = plt.subplots(figsize=(15, 4), constrained_layout=True)
                _ = ax.set_ylim(-2, 1.75)
                _ = ax.axhline(0, xmin=0.05, xmax=0.95, color='black', zorder=1)
                _ = ax.scatter(dates_ordered, np.zeros(len(dates_ordered)), s=120, c='black', zorder=2)
                _ = ax.scatter(dates_ordered, np.zeros(len(dates_ordered)), s=30, c='white', zorder=3)

                # Add in labels
                label_offsets = np.zeros(len(dates_ordered))
                label_offsets[::2] = 0.35
                label_offsets[1::2] = -0.7
                for i, (l, d) in enumerate(zip(labels, dates_ordered)):
                    _ = ax.text(d, label_offsets[i], l, ha='center', fontfamily='serif', fontweight='bold', color='black',fontsize=8)

                # Add in stems to link labels to associated points on the timeline 
                stems = np.zeros(len(dates_ordered))
                stems[::2] = 0.3
                stems[1::2] = -0.3   
                markerline, stemline, baseline = ax.stem(dates_ordered, stems)
                _ = plt.setp(markerline, marker=',', color='black')
                _ = plt.setp(stemline, color='black')

                # Hide lines around chart
                for spine in ["left", "top", "right", "bottom"]:
                    _ = ax.spines[spine].set_visible(False)
 
                # Hide tick labels and set title
                _ = ax.set_xticks([])
                _ = ax.set_yticks([])
                _ = ax.set_title('Research Timeline', fontweight="bold", fontfamily='serif', fontsize=12, 
                    color='black')

                # Save timeline on user computer as PDF using the file name they entered at the outset of the program
                plt.savefig(timeline_name)
                quit()

        # If user selects both, generate both CSV and research timeline (these are the same functions as above, so will not be annotated)
            elif output_format == 'Both' :
                import pandas as pd
                from glob import glob; from os.path import expanduser

                conn = sqlite3.connect(db_name)
                cur = conn.cursor()
                article_metadata = pd.read_sql('SELECT * FROM Articles ORDER BY Author, Date' ,conn)
                article_metadata.to_csv(csv_name, index=False)

                import matplotlib.pyplot as plt
                import numpy as np

                cur.execute('SELECT Date , Author FROM Articles')
                dates = cur.fetchall()
                date_strings = list()
                for da in dates :
                    datestr = ''.join(da)
                    datestr_format = datestr[:4] + '\n' + datestr[4:]
                    if datestr_format not in date_strings : date_strings.append(datestr_format)
                    dates_ordered = sorted(date_strings)
                conn.commit()
                conn.close()
          
                labels = dates_ordered

                fig, ax = plt.subplots(figsize=(15, 4), constrained_layout=True)
                _ = ax.set_ylim(-2, 1.75)
                _ = ax.axhline(0, xmin=0.05, xmax=0.95, c='black', zorder=1)
                _ = ax.scatter(dates_ordered, np.zeros(len(dates_ordered)), s=120, c='black', zorder=2)
                _ = ax.scatter(dates_ordered, np.zeros(len(dates_ordered)), s=30, c='white', zorder=3)

                label_offsets = np.zeros(len(dates_ordered))
                label_offsets[::2] = 0.35
                label_offsets[1::2] = -0.7
                for i, (l, d) in enumerate(zip(labels, dates_ordered)):
                    _ = ax.text(d, label_offsets[i], l, ha='center', fontfamily='serif', fontweight='bold', color='black',fontsize=8)

                stems = np.zeros(len(dates_ordered))
                stems[::2] = 0.3
                stems[1::2] = -0.3   
                markerline, stemline, baseline = ax.stem(dates_ordered, stems)
                _ = plt.setp(markerline, marker=',', color='black')
                _ = plt.setp(stemline, color='black')

                for spine in ["left", "top", "right", "bottom"]:
                    _ = ax.spines[spine].set_visible(False)
                _ = ax.set_xticks([])
                _ = ax.set_yticks([])
                _ = ax.set_title('Research Timeline', fontweight="bold", fontfamily='serif', fontsize=12, 
                        color='black')

                plt.savefig(timeline_name)
                quit()

# If user enters "old" as the type of project they would like to work on, ask for file name they will be adding to
    elif new_old == 'old' :
        project_name = input('\nPlease enter the name of the timeline project you would like to add to. Only enter the file name, without the format (e.g. only "file_name" not "file_name.db") ')
        db_name = project_name + '.db'
        csv_name = project_name + '.csv'
        timeline_name = project_name + '.pdf'

    # With the "old" option, the database does not need to be created so that step is skipped. Otherwise, the program is the exact same as the "new" option so it will not be annotated.
        import sqlite3 
        print('\nYou will now be repeatedly prompted to enter a file name or "Done." The file must be a ".txt" text file of an article citation with one or more authors. Once you are finished inputting research articles, enter "Done."')

        while True:

            fname = input('\nEnter file name or Done: ')
            if fname == 'Done' :
                break
            try :
                fhandle = open(fname)
            except :
                print('\nFile cannot be opened')
                continue

            lines = fhandle.readlines() 
            title = lines[1].rstrip()

            import re
            numlist = list()
            for line in lines:
                num = re.findall('\d{4}' , line)
                if num not in numlist : numlist.append(num)
            numlist = list(filter(None, numlist))
            select_date = numlist[0]
            convert_date = str(select_date)
            date = convert_date[2 : 6]

            authorlist = list()
            authorline = lines[0]
            persons = authorline.split(',')
            for person in persons:
                if person not in authorlist : authorlist.append(person)
            a = authorlist[0]
            a_split = a.split(' ')
            a_split.reverse()
            author = a_split[0] + ', ' + a_split[-1:][0]
    
            for line in lines:
                if line.startswith('https://d'):
                    doi = line

            conn = sqlite3.connect(db_name)
            cur = conn.cursor()
            cur.execute('''INSERT INTO Articles 
                    (Author, Date, Title, DOI) VALUES (?, ?, ?, ?)''',
                    (author, date, title, doi) )
            conn.commit()
            conn.close()

            continue

        print('\nPlease select the format(s) in which you would like your output.')

        while True:

            output_format = input('\nEnter "CSV" or "Timeline" or "Both": ')
            if output_format == 'CSV' or output_format =='Timeline' or output_format == 'Both' :
                print('\nYou have selected' , output_format)
            else : print('\nPlease enter valid output format.')

            if output_format == 'CSV' :
                import pandas as pd
                from glob import glob; from os.path import expanduser

                conn = sqlite3.connect(db_name)
                cur = conn.cursor()
                article_metadata = pd.read_sql('SELECT * FROM Articles ORDER BY Author, Date' ,conn)
                article_metadata.to_csv(csv_name, index=False)
                conn.close()
                quit()

            elif output_format == 'Timeline' :
                import matplotlib.pyplot as plt
                import numpy as np

                conn = sqlite3.connect(db_name)
                cur = conn.cursor()
                cur.execute('SELECT Date , Author FROM Articles')
                dates = cur.fetchall()
                date_strings = list()
                for da in dates :
                    datestr = ''.join(da)
                    datestr_format = datestr[:4] + '\n' + datestr[4:]
                    if datestr_format not in date_strings : date_strings.append(datestr_format)
                    dates_ordered = sorted(date_strings)
                conn.commit()
                conn.close()

                labels = dates_ordered

                fig, ax = plt.subplots(figsize=(15, 4), constrained_layout=True)
                _ = ax.set_ylim(-2, 1.75)
                _ = ax.axhline(0, xmin=0.05, xmax=0.95, color='royalblue', zorder=1)
                _ = ax.scatter(dates_ordered, np.zeros(len(dates_ordered)), s=120, c='black', zorder=2)
                _ = ax.scatter(dates_ordered, np.zeros(len(dates_ordered)), s=30, c='white', zorder=3)

                label_offsets = np.zeros(len(dates_ordered))
                label_offsets[::2] = 0.35
                label_offsets[1::2] = -0.7
                for i, (l, d) in enumerate(zip(labels, dates_ordered)):
                    _ = ax.text(d, label_offsets[i], l, ha='center', fontfamily='serif', fontweight='bold', color='black',fontsize=8)

                stems = np.zeros(len(dates_ordered))
                stems[::2] = 0.3
                stems[1::2] = -0.3   
                markerline, stemline, baseline = ax.stem(dates_ordered, stems)
                _ = plt.setp(markerline, marker=',', color='black')
                _ = plt.setp(stemline, color='black')

                for spine in ["left", "top", "right", "bottom"]:
                    _ = ax.spines[spine].set_visible(False) 
                _ = ax.set_xticks([])
                _ = ax.set_yticks([])
 
                _ = ax.set_title('Research Timeline', fontweight="bold", fontfamily='serif', fontsize=12, 
                    color='black')

                plt.savefig(timeline_name)
                quit()

            elif output_format == 'Both' :
                import pandas as pd
                from glob import glob; from os.path import expanduser

                conn = sqlite3.connect(db_name)
                cur = conn.cursor()
                article_metadata = pd.read_sql('SELECT * FROM Articles ORDER BY Author, Date' ,conn)
                article_metadata.to_csv(csv_name, index=False)

                import matplotlib.pyplot as plt
                import numpy as np

                cur.execute('SELECT Date , Author FROM Articles')
                dates = cur.fetchall()
                date_strings = list()
                for da in dates :
                    datestr = ''.join(da)
                    datestr_format = datestr[:4] + '\n' + datestr[4:]
                    if datestr_format not in date_strings : date_strings.append(datestr_format)
                    dates_ordered = sorted(date_strings)
                conn.commit()
                conn.close()
          
                labels = dates_ordered

                fig, ax = plt.subplots(figsize=(15, 4), constrained_layout=True)
                _ = ax.set_ylim(-2, 1.75)
                _ = ax.axhline(0, xmin=0.05, xmax=0.95, c='black', zorder=1)
                _ = ax.scatter(dates_ordered, np.zeros(len(dates_ordered)), s=120, c='black', zorder=2)
                _ = ax.scatter(dates_ordered, np.zeros(len(dates_ordered)), s=30, c='white', zorder=3)

                label_offsets = np.zeros(len(dates_ordered))
                label_offsets[::2] = 0.35
                label_offsets[1::2] = -0.7
                for i, (l, d) in enumerate(zip(labels, dates_ordered)):
                    _ = ax.text(d, label_offsets[i], l, ha='center', fontfamily='serif', fontweight='bold', color='black',fontsize=8)

                stems = np.zeros(len(dates_ordered))
                stems[::2] = 0.3
                stems[1::2] = -0.3   
                markerline, stemline, baseline = ax.stem(dates_ordered, stems)
                _ = plt.setp(markerline, marker=',', color='black')
                _ = plt.setp(stemline, color='black')

                for spine in ["left", "top", "right", "bottom"]:
                    _ = ax.spines[spine].set_visible(False)
                _ = ax.set_xticks([])
                _ = ax.set_yticks([])
 
                _ = ax.set_title('Research Timeline', fontweight="bold", fontfamily='serif', fontsize=12, 
                        color='black')

                plt.savefig(timeline_name)
                quit()
                
# If user enters any project type input that is neither "new" nor "old" the program will ask them again

    else : print('Please enter "new" or "old" ')
    continue