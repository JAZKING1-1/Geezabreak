from django.shortcuts import render
from django.http import JsonResponse
from .models import Feedback
from .models_comment import Comment
from django.core.mail import send_mail, EmailMessage

def home(request):
    if not request.session.get('visited_home'):
        request.session['visited_home'] = True
        request.session.save()
    comments = Comment.objects.filter(approved=True).order_by('-created_at')[:10]
    return render(request, 'main/home.html', {'comments': comments})

def landing(request):
    return render(request, 'main/landing.html')

def about(request):
    return render(request, 'main/about.html')

def services(request):
    return render(request, 'main/services.html')

def get_help(request):
    return render(request, 'main/get_help.html')

def submit_feedback(request):
    print("Feedback view called")
    if request.method == 'POST':
        try:
            feedback = Feedback(
                name=request.POST.get('name'),
                contact_number=request.POST.get('contact_number'),
                email=request.POST.get('email'),
                service_used=request.POST.get('service_used'),
                message=request.POST.get('message')
            )
            feedback.save()
            # Send feedback to email using EmailMessage with Reply-To
            subject = f"New Feedback from {feedback.name}"
            message = (
                f"Name: {feedback.name}\n"
                f"Contact Number: {feedback.contact_number}\n"
                f"Email: {feedback.email}\n"
                f"Service Used: {feedback.get_service_used_display()}\n"
                f"Message:\n{feedback.message}"
            )
            try:
                email = EmailMessage(
                    subject,
                    message,
                    'Geeza Break <ds16022004@gmail.com>',
                    ['ds16022004@gmail.com'],
                    headers={'Reply-To': feedback.email}
                )
                email.send(fail_silently=False)
            except Exception as e:
                print("EMAIL ERROR:", str(e))
                return JsonResponse({'status': 'error', 'message': f'Email error: {str(e)}'})
            return JsonResponse({'status': 'success', 'message': 'Thank you for your feedback!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def submit_comment(request):
    if request.method == 'POST':
        name = request.POST.get('name') or 'Anonymous'
        message = request.POST.get('message')
        if message:
            comment = Comment.objects.create(name=name, message=message)
            return JsonResponse({'status': 'success', 'name': comment.name, 'message': comment.message, 'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')})
        return JsonResponse({'status': 'error', 'message': 'Message is required.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def referral(request):
    return render(request, 'main/referral.html')

def fun_zone(request):
    games = [
        {'title': 'Memory Match', 'url': 'https://www.memozor.com/memory-games', 'thumb': 'images/games/memory.jpg', 'category': 'iq', 'desc': 'Improve your memory by matching cards!'},
        {'title': 'Math Playground', 'url': 'https://www.mathplayground.com/', 'thumb': 'images/games/math.jpg', 'category': 'iq', 'desc': 'Solve math puzzles and logic games.'},
        {'title': 'Simon Says', 'url': 'https://www.memozor.com/simon-game', 'thumb': 'images/games/simon.jpg', 'category': 'iq', 'desc': 'Repeat the color sequence.'},
        {'title': 'Sudoku for Kids', 'url': 'https://www.primarygames.com/puzzles/sudoku/', 'thumb': 'images/games/sudoku.jpg', 'category': 'iq', 'desc': 'Simple sudoku puzzles for beginners.'},
        {'title': 'Pattern Blocks', 'url': 'https://www.nctm.org/Classroom-Resources/Illuminations/Interactives/Pattern-Blocks/', 'thumb': 'images/games/pattern.jpg', 'category': 'iq', 'desc': 'Build and recognize patterns.'},
        {'title': 'Space Invaders', 'url': 'https://www.retrogames.cc/arcade-games/space-invaders.html', 'thumb': 'images/games/space-invaders.jpg', 'category': 'arcade', 'desc': 'Classic arcade shooter. Quick reflexes needed!'},
        {'title': 'Pac-Man', 'url': 'https://www.google.com/doodles/30th-anniversary-of-pac-man', 'thumb': 'images/games/pacman.jpg', 'category': 'arcade', 'desc': 'Eat the dots, avoid ghosts!'},
        {'title': 'Tetris', 'url': 'https://tetris.com/play-tetris', 'thumb': 'images/games/tetris.jpg', 'category': 'arcade', 'desc': 'Fit the falling blocks.'},
        {'title': 'Snake', 'url': 'https://playsnake.org/', 'thumb': 'images/games/snake.jpg', 'category': 'arcade', 'desc': 'Grow your snake, don’t hit the wall.'},
        {'title': 'Flappy Bird', 'url': 'https://flappybird.io/', 'thumb': 'images/games/flappy.jpg', 'category': 'arcade', 'desc': 'Tap to fly through pipes.'},
        {'title': 'Drawing Pad', 'url': 'https://sketch.io/sketchpad/', 'thumb': 'images/games/draw.jpg', 'category': 'creative', 'desc': 'Express creativity by painting online.'},
        {'title': 'Online Piano', 'url': 'https://www.onlinepianist.com/virtual-piano', 'thumb': 'images/games/piano.jpg', 'category': 'creative', 'desc': 'Play music with your keyboard.'},
        {'title': 'Coloring Book', 'url': 'https://www.thecolor.com/', 'thumb': 'images/games/coloring.jpg', 'category': 'creative', 'desc': 'Color fun pictures online.'},
        {'title': 'Make a Comic', 'url': 'https://www.makebeliefscomix.com/Comix/', 'thumb': 'images/games/comic.jpg', 'category': 'creative', 'desc': 'Create your own comic strips.'},
        {'title': 'LEGO Builder', 'url': 'https://www.lego.com/en-us/kids/build', 'thumb': 'images/games/lego.jpg', 'category': 'creative', 'desc': 'Build with virtual LEGO bricks.'},
        {'title': 'Jigsaw Puzzles', 'url': 'https://www.jigsawplanet.com/', 'thumb': 'images/games/jigsaw.jpg', 'category': 'puzzle', 'desc': 'Solve digital jigsaws.'},
        {'title': '2048', 'url': 'https://play2048.co/', 'thumb': 'images/games/2048.jpg', 'category': 'puzzle', 'desc': 'Slide tiles to reach 2048.'},
        {'title': 'Minesweeper', 'url': 'https://minesweeperonline.com/', 'thumb': 'images/games/minesweeper.jpg', 'category': 'puzzle', 'desc': 'Classic logic puzzle game.'},
        {'title': 'Tangram', 'url': 'https://www.transum.org/Maths/Investigation/Tangram/', 'thumb': 'images/games/tangram.jpg', 'category': 'puzzle', 'desc': 'Arrange shapes to match a picture.'},
        {'title': 'Chess for Kids', 'url': 'https://www.chesskid.com/play/fast', 'thumb': 'images/games/chess.jpg', 'category': 'strategy', 'desc': 'Play chess with hints and tips.'},
    ]
    return render(request, 'main/fun_zone.html', {'games': games})
