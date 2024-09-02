from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from Incident.models import Incident
from Incident.serializers import IncidentSerializer
from Incident.permissions import IsIncidentOwner
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from Incident.forms import IncidentForm
from django.views.generic import TemplateView, DetailView
from django.http import JsonResponse
from Incident.pagination import MyPageNumberPagination


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all().order_by('reported_date')
    serializer_class = IncidentSerializer
    permission_classes = [IsIncidentOwner]
    authentication_classes = [JWTAuthentication]
    pagination_class = MyPageNumberPagination

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Incident.objects.all().order_by('reported_date')
        return Incident.objects.filter(reporter=self.request.user).order_by('reported_date')


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response({
                "message": "Incident created successfully.",
                "data": serializer.data
            },  status=status.HTTP_201_CREATED)
        return Response({
                "error": "Unable to create incident. Please check the entered data.",
                "details": serializer.errors,
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response({"message": "Incident records fetched successfully.", "data": serializer.data})
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "message": "Incident records fetched successfully.",
            "data": serializer.data
        })


    def retrieve(self, request, pk=None):
        try:
            incident = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(incident)
            return Response({"message": "Incident retrieved successfully.", "data": serializer.data})
        except Incident.DoesNotExist:
            return Response({"error": "Incident not found with the provided ID."}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            incident = self.get_queryset().get(pk=pk)
            if incident.status == 'Closed':
                return Response({"detail": "Cannot edit a closed incident. The incident is already closed."}, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(incident, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Incident updated successfully.", "data": serializer.data})
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Incident.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        print("Request Data:", request.data) 
        try:
            incident = self.get_queryset().get(pk=pk)
            if incident.status == 'Closed':
                return Response({"error": "Cannot partially update incident. The incident is already closed."}, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(incident, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Incident.DoesNotExist:
            return Response({"error": "Incident not found with the provided ID."}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            incident = self.get_queryset().get(pk=pk)
            if incident.status == 'Closed' and not request.user.is_superuser:
                return Response({"detail": "Cannot delete a closed incident."}, status=status.HTTP_400_BAD_REQUEST)
            incident.delete()
            return Response({"message": "Incident deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Incident.DoesNotExist:
            return Response({"error": "Incident not found with the provided ID."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response({'error': 'Query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(incident_id__icontains=query)
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response({"message": "Search completed successfully.", "data": serializer.data})
        return Response({"message": "No incidents found matching the search criteria."})

    
    @action(detail=False, methods=['get'], url_path='search/suggestions')
    def suggestions(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response({'error': 'Query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        suggestions = self.get_queryset().filter(incident_id__icontains=query).values_list('incident_id', flat=True)[:5]
        return Response(suggestions)








class IncidentListView(TemplateView):
    template_name = 'incident/incident_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incidents'] = Incident.objects.all().order_by('-reported_date')
        return context

class IncidentFormView(View):
    template_name = 'incident/incident_form.html'

    def get(self, request, id=None):
        if id:
            incident = get_object_or_404(Incident, id=id)
            form = IncidentForm(instance=incident)
        else:
            form = IncidentForm()

        context = {
            'form': form,
            'id': id,
            'incident': incident if id else None,
        }
        return render(request, self.template_name, context)

    def post(self, request, id=None):
        if id:
            incident = get_object_or_404(Incident, id=id)
            form = IncidentForm(request.POST, instance=incident)
        else:
            form = IncidentForm(request.POST)

        if form.is_valid():
            incident = form.save(commit=False)
            incident.reporter = request.user
            incident.save()
            return redirect('incident_list')

        context = {
            'form': form,
            'id': id,
            'incident': incident if id else None,
        }
        return render(request, self.template_name, context)

    def patch(self, request, id=None):
        if id:
            incident = get_object_or_404(Incident, id=id)
            form = IncidentForm(request.POST, instance=incident)
            if form.is_valid():
                form.save()
                return JsonResponse({'message': 'Incident updated successfully'}, status=200)
            return JsonResponse(form.errors, status=400)
        return JsonResponse({'error': 'Incident ID is required'}, status=400)

class IncidentDetailView(DetailView):
    model = Incident
    template_name = 'incident/incident_detail.html'
    context_object_name = 'incident'

    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(Incident, id=id)

