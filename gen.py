import shutil
#using: rmtree

import os
#using: makedirs

import pandas as pd
#using read_csv, DataFrame, Series

import datetime as dt
#using: timedelta, datetime

import typing as ty
#using: Dict, List, Tuple

import more_itertools as mit
#using: peekable

legend: ty.Dict[str, str] = { 'xx': 'Distance Test @ Ambler Student Recreation Center Gym Floor' #{{{1
                            , 'y1': 'Tournament Round of 64 Begins @ Ambler Student Recreation Center'
                            , 'y2': 'Tournament Round of 32 Begins @ Ambler Student Recreation Center (Estimated)'
                            , 'y3': 'Tournament Sweet 16 Begins @ Ambler Student Recreation Center (Estimated'
                            , 'y4': 'Tournament Elite 8 Begins @ Ambler Student Recreation Center (Estimated)'
                            , 'y5': 'Tournament Final 4 Begins @ Ambler Student Recreation Center (Estimated)'
                            , 'y6': 'Tournament Championship Begins @ Ambler Student Recreation Center (Estimated)'
                            , 'p': 'Present @ Ambler Student Recreation Center 202'
                            , 'a': 'Present @ Ambler Student Recreation Center 203'
                            , 'u': 'Present @ LEEP2 1322'
                            , 'v': 'Present @ LEEP2 2326'
                            , 'l': 'Lunch @ Burge Union Forum D'
                            , 't': 'Engineering Complex Tour @ LEEP2 Atrium'
                            , 'i': 'Check-In Begins @ Burge Union'
                            , 'o': 'Opening Ceremony @ Burge Union Forum C/D'
                            , 'c': 'Closing Ceremony @ Burge Union Forum C/D'
                            , 'h': 'Hackathon @ Beren Petroleum Center'
                            , 'n': 'Present @ Slawson 194'
                            , 'm': 'Present @ Slawson 175'
                            , 'b': 'Build @ M2SEC G544'
                            } #1}}}

test_name: ty.Dict[str, str] = { 'chem': 'Heat Transfer Test @ Learned 3109' #{{{1
                               , 'bio': 'Demo and Test @ Learned 1100'
                               , 'civil': 'Structural Testing in front of M2SEC G548'
                               , 'meche': 'Test @ Burge Forum C'
                               } #1}}}

pres_name1: ty.Dict[str, str] = { 'chem': 'Present @ Ritchie 268' #{{{1
                               , 'bio': 'Present @ Slawson 298'
                               , 'civil': 'Present @ M2SEC G535'
                               , 'meche': 'Present @ Burge Forum C'
                               } #1}}}

pres_name2: ty.Dict[str, str] = { 'bio': 'Present @ Slawson 198' #{{{1
                               ,  'civil': 'Present @ M2SEC G530'
                               } #1}}}

comp_pretty_name: ty.Dict[str, str] = { 'bio': 'Biomedical Engineering' #{{{1
                                      , 'civil': 'Civil Engineering'
                                      , 'cs': 'Computer Science'
                                      , 'meche': 'Mechanical Engineering'
                                      , 'aero': 'Aerospace Engineering'
                                      , 'chem': 'Chemical Engineering'
                               } #1}}}

comps: ty.List[str] = [ 'bio' #{{{1
                      , 'aero'
                      , 'chem'
                      , 'cs'
                      , 'civil'
                      , 'meche'
                      ] #1}}}

def extract_schedule_data(raw_schedule_data: pd.Series, comp: str, step: int) -> ty.List[ty.Tuple[dt.datetime, str]]: #{{{1
    
    schedule = []

    start_hour: int = 7
    start_min: int = 30

    cur_time: dt.datetime = dt.datetime(2023, 10, 25, hour=start_hour, minute=start_min)
    schedule_gen: mit.more.peekable = mit.peekable(raw_schedule_data)

    for item in schedule_gen:
        # item != item => item == NaN since NaN != NaN as per the IEEE spec. Not the most type safe way of doing things but...
        if item != item or item.isspace():
            cur_time += dt.timedelta(minutes=step)
            continue
        if item == 'd':
            break
        try:
            if item in ['x', 'y', 'z']:
                match item:
                    case 'x':
                        schedule.append( (cur_time, test_name[comp]) )

                    case 'y':
                        schedule.append( (cur_time, pres_name1[comp]) )

                    case 'z':
                        schedule.append( (cur_time, pres_name2[comp]) )
            else:
                schedule.append( (cur_time,legend[item]) )

            while item == schedule_gen.peek():
                cur_time += dt.timedelta(minutes=step)
                next(schedule_gen)
            cur_time += dt.timedelta(minutes=step)

        except KeyError:
            raise RuntimeError(f'Invalid item: "{item}" in {comp}!')

    return schedule
#1}}}

def texify_schedule(schedule_data: ty.List[ty.Tuple[dt.datetime, str]]) -> str: #{{{1
    tex = '\\begin{center}\n\\begin{tabular}{c|c}\nTime & Event\\\\\n\\toprule\n'
    for idx, item in enumerate(schedule_data):
        tex += f'{item[0].strftime("%I:%M %p")}&{item[1]}\\\\\n'
        if idx != len(schedule_data)-1:
            tex+='\\midrule\n'
    tex += '\\bottomrule\n\end{tabular}\n\end{center}'
    return tex
#1}}}

def generate_pdf_tex(schedule_tex: str, team_num: str, team_name: str, comp: str) -> str: #{{{1
    preamble = """
\\documentclass[12pt]{article}

\\usepackage[letterpaper, margin=1in]{geometry}
\\usepackage{booktabs}
\\usepackage[center]{titlesec}
    """
    header='\section*{' + comp_pretty_name[comp] + ' Team \#' + team_num + '\\\\\\textit{\\footnotesize ' + team_name.replace('&','\&') + '}}\n'

    return preamble + '\\begin{document}\n' + header + schedule_tex + '\n\\end{document}'
#1}}}

def main() -> None: #{{{1
    
    for comp in comps:

        print(f'Creating schedules for {comp} competition.')

        shutil.rmtree(f'schedules/{comp}/tex')
        os.makedirs(f'schedules/{comp}/tex')

        df: pd.DataFrame = pd.read_csv(f'inputs/{comp}.csv').transpose()

        #the type here is complicated enough I don't really want to type hint it atm.
        row_gen = df.iterrows()
        team_names = pd.read_csv(f'registrants/{comp}.csv')

        next(row_gen)
        
        team_num = 1

        for team in row_gen:
            if not team[0].isdigit():
                break

            print(f'Generating schedule for team {team_num}...')
            
            try:
                team_name = team_names['Team Names'][team_num-1]
                #testing for NaN...
                if team_name != team_name:
                    team_name = team_names['School'][team_num-1]
            except KeyError:
                raise KeyError(f'Maybe mismatch between number of team names and number of teams on schedule for {comp}?')

            with open(f'schedules/{comp}/tex/{team_num}_{team_name.replace(" ", "_").replace("?", "").replace("/", "").replace("&","and")}.tex','w') as texfile:
                print('Extracting data...')
                
                step = 10 if comp in ['bio', 'chem'] else 5
                schedule_data = extract_schedule_data(team[1], comp, step)

                print('Generating schedule TeX...')
                schedule_tex = texify_schedule(schedule_data)

                print('Creating TeX document...')
                pdf_tex = generate_pdf_tex(schedule_tex, str(team_num), team_name, comp)
                texfile.write(pdf_tex)
            team_num += 1
    print('Done creating TeX for all schedules!')
#1}}}

main()
