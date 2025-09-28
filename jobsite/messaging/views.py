from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Message
from .forms import MessageForm

User = get_user_model()

@login_required
def inbox(request):
    # Get all messages where the user is either sender or recipient
    all_messages = Message.objects.filter(Q(recipient=request.user) | Q(sender=request.user)).order_by('-timestamp')

    # Group messages by thread (root message)
    threads = {}
    for message in all_messages:
        root_message = message
        while root_message.parent_message:
            root_message = root_message.parent_message
        
        if root_message.id not in threads:
            threads[root_message.id] = {
                'root_subject': root_message.subject,
                'messages': [],
                'sent_by_user': False,
                'received_by_user': False
            }
        threads[root_message.id]['messages'].append(message)
        if message.sender == request.user:
            threads[root_message.id]['sent_by_user'] = True
        if message.recipient == request.user:
            threads[root_message.id]['received_by_user'] = True
    
    # For each thread, get the most recent message and categorize
    sent_threads_data = []
    received_threads_data = []

    for thread_data in threads.values():
        messages = thread_data['messages']
        latest_message_in_thread = max(messages, key=lambda m: m.timestamp)
        
        thread_info = {
            'latest_message': latest_message_in_thread,
            'root_subject': thread_data['root_subject']
        }

        if thread_data['sent_by_user']:
            sent_threads_data.append(thread_info)
        if thread_data['received_by_user']:
            received_threads_data.append(thread_info)
    
    # Sort latest messages by timestamp for both categories
    sent_threads_data.sort(key=lambda x: x['latest_message'].timestamp, reverse=True)
    received_threads_data.sort(key=lambda x: x['latest_message'].timestamp, reverse=True)

    return render(request, 'messaging/inbox.html', {
        'sent_threads_data': sent_threads_data,
        'received_threads_data': received_threads_data,
    })

@login_required
def compose_message(request, recipient_id=None):
    recipient = None
    if recipient_id:
        recipient = get_object_or_404(User, id=recipient_id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient if recipient else form.cleaned_data['recipient']
            message.save()
            return redirect('messaging:inbox')
    else:
        form = MessageForm(initial={'recipient': recipient})
    return render(request, 'messaging/compose_message.html', {'form': form, 'recipient': recipient})

@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, (Q(recipient=request.user) | Q(sender=request.user)), id=message_id)
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.save()
    
    # Find the root message of the thread
    root_message = message
    while root_message.parent_message:
        root_message = root_message.parent_message

    # Get all messages in the thread, including the root and all its replies, ordered by newest first
    thread_messages_set = set()
    
    def get_all_descendants(msg):
        thread_messages_set.add(msg)
        for reply in msg.replies.all():
            get_all_descendants(reply)

    get_all_descendants(root_message)
    
    thread_messages = sorted(list(thread_messages_set), key=lambda m: m.timestamp)

    initial_recipient = message.recipient if message.sender == request.user else message.sender
    
    # Handle reply functionality
    if request.method == 'POST':
        reply_form = MessageForm(request.POST, parent_message=message)
        if reply_form.is_valid():
            reply_message_instance = reply_form.save(commit=False)
            reply_message_instance.sender = request.user
            reply_message_instance.recipient = initial_recipient
            reply_message_instance.subject = root_message.subject
            reply_message_instance.parent_message = message
            reply_message_instance.save()
            
            return redirect('messaging:view_message', message_id=root_message.id)
    else:
        reply_form = MessageForm(initial={'recipient': initial_recipient}, parent_message=message)

    return render(request, 'messaging/view_message.html', {
        'message': message,
        'thread_messages': thread_messages,
        'root_subject': root_message.subject,
        'reply_form': reply_form,
        'initial_recipient': initial_recipient,
    })
