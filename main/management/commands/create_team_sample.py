from django.core.management.base import BaseCommand
from main.models import TeamMember

class Command(BaseCommand):
    help = 'Creates sample team members for demonstration purposes'

    def handle(self, *args, **kwargs):
        team_members_data = [
            {
                'name': 'John Smith',
                'role_title': 'Board Chairperson',
                'joined_date': 'January 2018',
                'reason_for_joining': 'Having witnessed the impact of family support services in my community, I was inspired to contribute to Geeza Break\'s mission of strengthening families across Glasgow.',
                'role_description': 'As Chairperson, I lead board meetings, work closely with the CEO, and ensure our governance meets the highest standards while supporting our strategic direction.',
                'favorite_aspect': 'Seeing the tangible impact our services have on families and watching children thrive with the support we provide.',
                'fun_fact': 'I\'m an amateur baker and often bring my latest experiments to board meetings. My sourdough has a mixed reception!',
                'order': 1
            },
            {
                'name': 'Sarah Williams',
                'role_title': 'Treasurer',
                'joined_date': 'March 2019',
                'reason_for_joining': 'With my financial background, I wanted to use my skills to help a charity making real difference in Glasgow. The values and community focus of Geeza Break immediately resonated with me.',
                'role_description': 'I oversee the financial health of the organization, work on budgeting, and ensure we have strong financial controls while maximizing the impact of every pound.',
                'favorite_aspect': 'Working with a team that is genuinely passionate about helping families and seeing how responsible financial management translates into more children and families supported.',
                'fun_fact': 'When I need a break, I go wild swimming in Scottish lochs, regardless of the weather!',
                'order': 2
            },
            {
                'name': 'Mohammed Khan',
                'role_title': 'Secretary',
                'joined_date': 'October 2020',
                'reason_for_joining': 'As a father of three, I understand the challenges of parenting and wanted to support an organization that helps families during difficult times.',
                'role_description': 'I manage board documentation, ensure compliance with regulatory requirements, and help maintain effective communication between the board and staff.',
                'favorite_aspect': 'The collaborative atmosphere where everyone shares ideas freely and works together to improve our services.',
                'fun_fact': 'I\'m a dedicated marathon runner and use my races to raise awareness and funds for Geeza Break.',
                'order': 3
            },
            {
                'name': 'Fiona MacLeod',
                'role_title': 'Trustee - HR Specialist',
                'joined_date': 'May 2021',
                'reason_for_joining': 'I was looking to use my HR expertise in a meaningful way, and Geeza Break\'s commitment to both its staff and service users impressed me.',
                'role_description': 'I provide guidance on HR policies, staff development, and ensuring we create a supportive environment for our team so they can best serve our families.',
                'favorite_aspect': 'Seeing staff grow in their roles and develop innovative approaches to supporting vulnerable families.',
                'fun_fact': 'I have a collection of over 300 snow globes from places I\'ve visited around the world.',
                'order': 4
            },
            {
                'name': 'David Chen',
                'role_title': 'Trustee - Community Engagement',
                'joined_date': 'February 2020',
                'reason_for_joining': 'Having grown up in Glasgow\'s East End, I\'ve seen firsthand how organizations like Geeza Break can transform communities.',
                'role_description': 'I focus on strengthening our community partnerships, increasing our visibility, and ensuring we remain responsive to evolving community needs.',
                'favorite_aspect': 'Hearing success stories from families who have rebuilt their lives with our support.',
                'fun_fact': 'I play in a local folk band and sometimes bring my fiddle to family fun days.',
                'order': 5
            },
            {
                'name': 'Aisha Patel',
                'role_title': 'Trustee - Child Welfare',
                'joined_date': 'September 2019',
                'reason_for_joining': 'As a pediatrician, I wanted to contribute to an organization that takes a holistic approach to child wellbeing.',
                'role_description': 'I advise on child development aspects of our services and help ensure our programs address the diverse needs of children we support.',
                'favorite_aspect': 'Seeing children gain confidence and resilience through our tailored support programs.',
                'fun_fact': 'I\'m a keen gardener and have converted my entire back garden into a vegetable patch.',
                'order': 6
            },
            {
                'name': 'Robert Campbell',
                'role_title': 'Trustee - Legal Affairs',
                'joined_date': 'April 2022',
                'reason_for_joining': 'I wanted to use my legal expertise to help safeguard and strengthen an organization doing vital work for Glasgow families.',
                'role_description': 'I provide guidance on legal matters, review contracts and agreements, and help navigate regulatory requirements.',
                'favorite_aspect': 'Being part of a team that approaches challenges creatively and always puts families first.',
                'fun_fact': 'I\'m a certified scuba diving instructor and spend most of my holidays underwater.',
                'order': 7
            },
            {
                'name': 'Elena Kowalski',
                'role_title': 'Trustee - Program Development',
                'joined_date': 'July 2021',
                'reason_for_joining': 'With my background in social work, I wanted to help shape services that truly meet the needs of vulnerable families.',
                'role_description': 'I work on evaluating our current programs, identifying gaps in services, and developing new initiatives to better serve our community.',
                'favorite_aspect': 'The innovation and flexibility of Geeza Break in adapting to changing family needs.',
                'fun_fact': 'I\'m writing a children\'s book series about a family of hedgehogs who help their neighbors.',
                'order': 8
            },
            {
                'name': 'Thomas Wilson',
                'role_title': 'Trustee - Fundraising',
                'joined_date': 'December 2020',
                'reason_for_joining': 'I wanted to use my background in corporate partnerships to help secure sustainable funding for vital family services.',
                'role_description': 'I lead on developing our fundraising strategy, cultivating donor relationships, and identifying new funding opportunities.',
                'favorite_aspect': 'Seeing how our supporters become genuinely invested in the welfare of our families and the success of our organization.',
                'fun_fact': 'I\'m a competitive ballroom dancer and have won several Scottish championships.',
                'order': 9
            },
            {
                'name': 'Grace Osei',
                'role_title': 'Trustee - Digital Strategy',
                'joined_date': 'August 2022',
                'reason_for_joining': 'I was impressed by Geeza Break\'s commitment to reaching families in new ways and wanted to help drive their digital transformation.',
                'role_description': 'I advise on our digital presence, help improve accessibility of our services online, and explore new technologies to enhance our impact.',
                'favorite_aspect': 'The willingness to embrace change and try new approaches to better serve our community.',
                'fun_fact': 'I host a podcast about technology for social good and have interviewed over 100 social entrepreneurs.',
                'order': 10
            }
        ]

        # Clear existing team members
        TeamMember.objects.all().delete()
        
        # Create new team members
        for data in team_members_data:
            TeamMember.objects.create(**data)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(team_members_data)} team members'))
