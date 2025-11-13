from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from mail.models import Contact, Project, Task, Document
from organizations.models import Organization


@login_required
def dashboard(request):
    """Business dashboard view"""
    try:
        organization = getattr(request.user, 'organization', None)
        if not organization:
            messages.error(request, 'You are not associated with any organization.')
            return redirect('mail:inbox')

        # Get user's business data
        contacts = Contact.objects.filter(user=request.user)[:10]
        projects = Project.objects.filter(organization=organization, created_by=request.user)[:10]
        tasks = Task.objects.filter(organization=organization, created_by=request.user)[:10]
        documents = Document.objects.filter(uploaded_by=request.user)[:10]

        context = {
            'contacts': contacts,
            'projects': projects,
            'tasks': tasks,
            'documents': documents,
            'organization': organization,
        }

        return render(request, 'business/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('mail:inbox')


# Contact views
@login_required
def contact_list(request):
    """List all contacts"""
    organization = getattr(request.user, 'organization', None)
    if not organization:
        messages.error(request, 'You are not associated with any organization.')
        return redirect('business:dashboard')

    contacts = Contact.objects.filter(user=request.user)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        contacts = contacts.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(company__icontains=search_query)
        )

    # Tag filtering
    tag_filter = request.GET.get('tag', '')
    if tag_filter:
        contacts = contacts.filter(tags__icontains=tag_filter)

    context = {
        'contacts': contacts,
        'search_query': search_query,
        'tag_filter': tag_filter,
    }
    return render(request, 'business/contacts/list.html', context)


@login_required
def contact_detail(request, contact_id):
    """View contact details"""
    organization = getattr(request.user, 'organization', None)
    contact = get_object_or_404(
        Contact,
        id=contact_id,
        organization=organization,
        user=request.user
    )

    context = {
        'contact': contact,
    }
    return render(request, 'business/contacts/detail.html', context)


@login_required
def contact_create(request):
    """Create new contact"""
    organization = getattr(request.user, 'organization', None)
    if not organization:
        messages.error(request, 'You are not associated with any organization.')
        return redirect('business:dashboard')

    if request.method == 'POST':
        try:
            contact = Contact.objects.create(
                user=request.user,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone', ''),
                company=request.POST.get('company', ''),
                job_title=request.POST.get('job_title', ''),
                address=request.POST.get('address', ''),
                notes=request.POST.get('notes', ''),
                tags=request.POST.getlist('tags', []),
                source='manual'
            )
            messages.success(request, f'Contact {contact.full_name} created successfully.')
            return redirect('business:contact_detail', contact_id=contact.id)
        except Exception as e:
            messages.error(request, f'Error creating contact: {str(e)}')

    return render(request, 'business/contacts/create.html')


@login_required
def contact_edit(request, contact_id):
    """Edit existing contact"""
    organization = getattr(request.user, 'organization', None)
    contact = get_object_or_404(
        Contact,
        id=contact_id,
        organization=organization,
        user=request.user
    )

    if request.method == 'POST':
        try:
            contact.first_name = request.POST.get('first_name')
            contact.last_name = request.POST.get('last_name')
            contact.email = request.POST.get('email')
            contact.phone = request.POST.get('phone', '')
            contact.company = request.POST.get('company', '')
            contact.job_title = request.POST.get('job_title', '')
            contact.address = request.POST.get('address', '')
            contact.notes = request.POST.get('notes', '')
            contact.tags = request.POST.getlist('tags', [])
            contact.save()

            messages.success(request, f'Contact {contact.full_name} updated successfully.')
            return redirect('business:contact_detail', contact_id=contact.id)
        except Exception as e:
            messages.error(request, f'Error updating contact: {str(e)}')

    context = {
        'contact': contact,
    }
    return render(request, 'business/contacts/edit.html', context)


@login_required
@require_POST
def contact_delete(request, contact_id):
    """Delete contact"""
    organization = getattr(request.user, 'organization', None)
    contact = get_object_or_404(
        Contact,
        id=contact_id,
        organization=organization,
        user=request.user
    )

    try:
        contact.delete()
        messages.success(request, f'Contact {contact.full_name} deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting contact: {str(e)}')

    return redirect('business:contact_list')


# Project views
@login_required
def project_list(request):
    """List all projects"""
    organization = getattr(request.user, 'organization', None)
    if not organization:
        messages.error(request, 'You are not associated with any organization.')
        return redirect('business:dashboard')

    projects = Project.objects.filter(organization=organization, created_by=request.user)

    # Status filtering
    status_filter = request.GET.get('status', '')
    if status_filter:
        projects = projects.filter(status=status_filter)

    context = {
        'projects': projects,
        'status_filter': status_filter,
        'status_choices': Project._meta.get_field('status').choices,
    }
    return render(request, 'business/projects/list.html', context)


@login_required
def project_detail(request, project_id):
    """View project details"""
    organization = getattr(request.user, 'organization', None)
    project = get_object_or_404(
        Project,
        id=project_id,
        organization=organization,
        created_by=request.user
    )

    tasks = Task.objects.filter(project=project)
    documents = Document.objects.filter(project=project)

    context = {
        'project': project,
        'tasks': tasks,
        'documents': documents,
    }
    return render(request, 'business/projects/detail.html', context)


@login_required
def project_create(request):
    """Create new project"""
    organization = getattr(request.user, 'organization', None)
    if not organization:
        messages.error(request, 'You are not associated with any organization.')
        return redirect('business:dashboard')

    if request.method == 'POST':
        try:
            project = Project.objects.create(
                created_by=request.user,
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                status=request.POST.get('status', 'planning'),
                start_date=request.POST.get('start_date') or None,
                end_date=request.POST.get('end_date') or None,
                budget=request.POST.get('budget') or None
            )

            # Add team members
            team_member_ids = request.POST.getlist('team_members')
            if team_member_ids:
                project.team_members.set(team_member_ids)

            messages.success(request, f'Project "{project.name}" created successfully.')
            return redirect('business:project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')

    # Get available users for assignment
    available_users = []
    if organization:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        available_users = User.objects.filter(organization=organization, is_active=True)

    context = {
        'status_choices': Project._meta.get_field('status').choices,
        'available_users': available_users,
    }
    return render(request, 'business/projects/create.html', context)


@login_required
def project_edit(request, project_id):
    """Edit existing project"""
    organization = getattr(request.user, 'organization', None)
    project = get_object_or_404(
        Project,
        id=project_id,
        organization=organization,
        created_by=request.user
    )

    if request.method == 'POST':
        try:
            project.name = request.POST.get('name')
            project.description = request.POST.get('description', '')
            project.status = request.POST.get('status', 'planning')
            project.start_date = request.POST.get('start_date') or None
            project.end_date = request.POST.get('end_date') or None
            project.budget = request.POST.get('budget') or None
            project.save()

            # Update team members
            team_member_ids = request.POST.getlist('team_members')
            project.team_members.set(team_member_ids)

            messages.success(request, f'Project "{project.name}" updated successfully.')
            return redirect('business:project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'Error updating project: {str(e)}')

    # Get available users for assignment
    available_users = []
    if organization:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        available_users = User.objects.filter(organization=organization, is_active=True)

    context = {
        'project': project,
        'status_choices': Project._meta.get_field('status').choices,
        'available_users': available_users,
    }
    return render(request, 'business/projects/edit.html', context)


@login_required
@require_POST
def project_delete(request, project_id):
    """Delete project"""
    organization = getattr(request.user, 'organization', None)
    project = get_object_or_404(
        Project,
        id=project_id,
        organization=organization,
        created_by=request.user
    )

    try:
        project.delete()
        messages.success(request, f'Project "{project.name}" deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting project: {str(e)}')

    return redirect('business:project_list')


# Task views
@login_required
def task_list(request):
    """List all tasks"""
    organization = getattr(request.user, 'organization', None)
    if not organization:
        messages.error(request, 'You are not associated with any organization.')
        return redirect('business:dashboard')

    tasks = Task.objects.filter(organization=organization, created_by=request.user)

    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    project_filter = request.GET.get('project', '')
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)

    context = {
        'tasks': tasks,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'project_filter': project_filter,
        'status_choices': Task._meta.get_field('status').choices,
        'priority_choices': Task._meta.get_field('priority').choices,
        'projects': Project.objects.filter(organization=organization, created_by=request.user),
    }
    return render(request, 'business/tasks/list.html', context)


@login_required
def task_detail(request, task_id):
    """View task details"""
    organization = getattr(request.user, 'organization', None)
    task = get_object_or_404(
        Task,
        id=task_id,
        organization=organization,
        created_by=request.user
    )

    context = {
        'task': task,
    }
    return render(request, 'business/tasks/detail.html', context)


@login_required
def task_create(request):
    """Create new task"""
    organization = getattr(request.user, 'organization', None)
    if not organization:
        messages.error(request, 'You are not associated with any organization.')
        return redirect('business:dashboard')

    if request.method == 'POST':
        try:
            task = Task.objects.create(
                created_by=request.user,
                assigned_to_id=request.POST.get('assigned_to'),  # Required field
                project_id=request.POST.get('project') or None,
                title=request.POST.get('title'),
                description=request.POST.get('description', ''),
                status=request.POST.get('status', 'todo'),
                priority=request.POST.get('priority', 'medium'),
                due_date=request.POST.get('due_date') or None
            )

            messages.success(request, f'Task "{task.title}" created successfully.')
            return redirect('business:task_detail', task_id=task.id)
        except Exception as e:
            messages.error(request, f'Error creating task: {str(e)}')

    # Get available projects and users
    projects = Project.objects.filter(organization=organization, created_by=request.user)
    # Get all users in the same organization
    available_users = []
    if organization:
        # Since organization.users is a reverse relation, we need to get users who have this organization
        from django.contrib.auth import get_user_model
        User = get_user_model()
        available_users = User.objects.filter(organization=organization, is_active=True)

    context = {
        'status_choices': Task._meta.get_field('status').choices,
        'priority_choices': Task._meta.get_field('priority').choices,
        'projects': projects,
        'available_users': available_users,
    }
    return render(request, 'business/tasks/create.html', context)


@login_required
def task_edit(request, task_id):
    """Edit existing task"""
    organization = getattr(request.user, 'organization', None)
    task = get_object_or_404(
        Task,
        id=task_id,
        organization=organization,
        created_by=request.user
    )

    if request.method == 'POST':
        try:
            task.project_id = request.POST.get('project') or None
            task.title = request.POST.get('title')
            task.description = request.POST.get('description', '')
            task.status = request.POST.get('status', 'todo')
            task.priority = request.POST.get('priority', 'medium')
            task.due_date = request.POST.get('due_date') or None
            task.assigned_to_id = request.POST.get('assigned_to')  # Required field
            task.save()

            messages.success(request, f'Task "{task.title}" updated successfully.')
            return redirect('business:task_detail', task_id=task.id)
        except Exception as e:
            messages.error(request, f'Error updating task: {str(e)}')

    # Get available projects and users
    projects = Project.objects.filter(organization=organization, created_by=request.user)
    # Get all users in the same organization
    available_users = []
    if organization:
        # Since organization.users is a reverse relation, we need to get users who have this organization
        from django.contrib.auth import get_user_model
        User = get_user_model()
        available_users = User.objects.filter(organization=organization, is_active=True)

    context = {
        'task': task,
        'status_choices': Task._meta.get_field('status').choices,
        'priority_choices': Task._meta.get_field('priority').choices,
        'projects': projects,
        'available_users': available_users,
    }
    return render(request, 'business/tasks/edit.html', context)


@login_required
@require_POST
def task_delete(request, task_id):
    """Delete task"""
    organization = getattr(request.user, 'organization', None)
    task = get_object_or_404(
        Task,
        id=task_id,
        organization=organization,
        created_by=request.user
    )

    try:
        task.delete()
        messages.success(request, f'Task "{task.title}" deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting task: {str(e)}')

    return redirect('business:task_list')


# Document views
@login_required
def document_list(request):
    """List all documents"""
    organization = getattr(request.user, 'organization', None)
    if not organization:
        messages.error(request, 'You are not associated with any organization.')
        return redirect('business:dashboard')

    documents = Document.objects.filter(uploaded_by=request.user)

    # Filters
    type_filter = request.GET.get('type', '')
    if type_filter:
        documents = documents.filter(category=type_filter)

    project_filter = request.GET.get('project', '')
    if project_filter:
        documents = documents.filter(project_id=project_filter)

    context = {
        'documents': documents,
        'type_filter': type_filter,
        'project_filter': project_filter,
        'document_types': Document._meta.get_field('category').choices,
        'projects': Project.objects.filter(organization=organization, created_by=request.user),
    }
    return render(request, 'business/documents/list.html', context)


@login_required
def document_detail(request, document_id):
    """View document details"""
    organization = getattr(request.user, 'organization', None)
    document = get_object_or_404(
        Document,
        id=document_id,
        organization=organization,
        uploaded_by=request.user
    )

    context = {
        'document': document,
    }
    return render(request, 'business/documents/detail.html', context)


@login_required
def document_create(request):
    """Create new document"""
    organization = getattr(request.user, 'organization', None)
    if not organization:
        messages.error(request, 'You are not associated with any organization.')
        return redirect('business:dashboard')

    if request.method == 'POST':
        try:
            uploaded_file = request.FILES.get('file')
            document = Document.objects.create(
                uploaded_by=request.user,
                title=request.POST.get('title'),
                description=request.POST.get('description', ''),
                category=request.POST.get('category', 'other'),
                file=uploaded_file,
                file_name=uploaded_file.name if uploaded_file else '',
                file_size=uploaded_file.size if uploaded_file else 0,
                mime_type=uploaded_file.content_type if uploaded_file else '',
                project_id=request.POST.get('project') or None,
                contact_id=request.POST.get('contact') or None,
                tags=request.POST.getlist('tags', []),
                version=int(request.POST.get('version', '1')),
                is_public=request.POST.get('is_public') == 'on'
            )

            messages.success(request, f'Document "{document.title}" uploaded successfully.')
            return redirect('business:document_detail', document_id=document.id)
        except Exception as e:
            messages.error(request, f'Error uploading document: {str(e)}')

    # Get available projects and contacts
    projects = Project.objects.filter(organization=organization, created_by=request.user)
    contacts = Contact.objects.filter(user=request.user)

    context = {
        'document_types': Document._meta.get_field('category').choices,
        'projects': projects,
        'contacts': contacts,
    }
    return render(request, 'business/documents/create.html', context)


@login_required
@require_POST
def document_delete(request, document_id):
    """Delete document"""
    organization = getattr(request.user, 'organization', None)
    document = get_object_or_404(
        Document,
        id=document_id,
        organization=organization,
        uploaded_by=request.user
    )

    try:
        document.delete()
        messages.success(request, f'Document "{document.title}" deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting document: {str(e)}')

    return redirect('business:document_list')
