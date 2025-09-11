from django.core.management.base import BaseCommand
from main.models import TeamMember

class Command(BaseCommand):
    help = 'Creates the 4 board member team members for the website'

    def handle(self, *args, **kwargs):
        team_members_data = [
            {
                'name': 'Mark Mulholland',
                'role_title': 'Treasurer',
                'joined_date': '2009',  # 15 years since 2009
                'reason_for_joining': 'I wanted to support the local community and be involved in a great grassroots organisation that provides much needed practical support for children and families',
                'role_description': 'working alongside the CEO, the fellow Trustees and the Finance Officer to oversee the strategy, direction, and good governance of the organisation. Promoting the organisation and telling the impact of the services that support local people in the local northeast communities. Supporting fundraising activities.',
                'favorite_aspect': 'the variety involved in being part of such a long-standing organisation that really puts children, young people, and families at the heart of its services',
                'fun_fact': 'Go to the football and spending quality time with my family',
                'order': 1
            },
            {
                'name': 'Elaine Mitchell',
                'role_title': 'Board Member',
                'joined_date': '2018',  # 6 years since 2018
                'reason_for_joining': 'Having witnessed the impact of family support services in my community, I was inspired to contribute to Geeza Break\'s mission of strengthening families across Glasgow.',
                'role_description': 'I focus on strengthening our community partnerships, increasing our visibility, and ensuring we remain responsive to evolving community needs.',
                'favorite_aspect': 'Seeing the tangible impact our services have on families and watching children thrive with the support we provide.',
                'fun_fact': 'I love gardening and have converted my entire back garden into a vegetable patch.',
                'order': 2
            },
            {
                'name': 'Nancy Ross',
                'role_title': 'Board Member',
                'joined_date': 'January 2024',
                'reason_for_joining': 'As a mother, I understand the challenges of parenting and wanted to support an organization that helps families during difficult times.',
                'role_description': 'I provide guidance on HR policies, staff development, and ensuring we create a supportive environment for our team so they can best serve our families.',
                'favorite_aspect': 'The collaborative atmosphere where everyone shares ideas freely and works together to improve our services.',
                'fun_fact': 'I\'m a keen baker and often bring my latest experiments to meetings.',
                'order': 3
            },
            {
                'name': 'Derek Sinclair',
                'role_title': 'Chairperson',
                'joined_date': '2009',
                'reason_for_joining': 'I wanted to support the local community and be involved in a great grassroots organisation that provides much needed practical support for children and families',
                'role_description': 'working alongside the CEO, my fellow Trustees and the Finance Officer to oversee the strategy, direction, and good governance of the organisation. Promoting the organisation and telling the impact of the services that support local people in the local northeast communities. Supporting fundraising activities.',
                'favorite_aspect': 'the variety involved in being part of such a long-standing organisation that really puts children, young people, and families at the heart of its services',
                'fun_fact': 'Go to the football and spending quality time with my family',
                'order': 4
            }
        ]

        # Clear existing team members
        TeamMember.objects.all().delete()
        
        # Create new team members
        for data in team_members_data:
            TeamMember.objects.create(**data)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(team_members_data)} board member team members'))
