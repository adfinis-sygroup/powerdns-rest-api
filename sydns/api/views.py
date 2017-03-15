from sydns.api.models import Domain, Record, Zone, User
from sydns.api.serializers import DomainSerializer, RecordSerializer, ZoneSerializer
from rest_framework import viewsets, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'domains': reverse('domain-list', request=request, format=format),
        'records': reverse('record-list', request=request, format=format),
    })


class DomainViewSet(viewsets.ModelViewSet):
    """
    This viewset provides actions around `domains`.
    """
    serializer_class = DomainSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "name"

    def get_queryset(self):
        '''Only return domains which the user is allowed to manage.

        '''
        owner = User.objects.get(username=self.request.user.username)
        allowed_zones = [zone.id for zone in Zone.objects.filter(owner=owner.id)]

        return Domain.objects.filter(pk__in=allowed_zones)

    def create(self, request):
        """
        Link user to the created domain through a record in the in the intermediate "zones" table.
        """
        owner = User.objects.get(username=request.user.username)

        domain_serializer = DomainSerializer(data=request.data)
        domain_serializer.is_valid()
        domain = domain_serializer.save()

        zone = ZoneSerializer(data={'domain_id': domain.id, 'owner': owner.id})
        zone.is_valid()
        zone.save()

        return Response(domain_serializer.data, status=status.HTTP_201_CREATED)

class RecordList(generics.ListCreateAPIView):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = (IsAuthenticated,)

class RecordDetail(generics.RetrieveUpdateAPIView):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = (IsAuthenticated,)
