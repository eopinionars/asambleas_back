from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import boto3
import os

from .seriaizers import EventoSerializer, PregAbiertaSerializer, PregDecimalSerializer, PregMultipleSerializer, \
    OpcionMultipleSerializer, DocumentoSerializer, QuorumSerializer
from .models import Evento, PreguntaAbierta, PreguntaDecimal, PreguntaMultiple, OpcionesMultiple,\
    Documentos, Quorum, InmueblesQuorum
from usuarios.models import Asambleista, Apoderado


def deleteBucketObjects(files):
    # Connection to bucket
    AWS_ACCESS_KEY_ID = os.environ.get(
        'BUCKETEER_AWS_ACCESS_KEY_ID', None)
    AWS_SECRET_ACCESS_KEY = os.environ.get(
        'BUCKETEER_AWS_SECRET_ACCESS_KEY', None)
    AWS_STORAGE_BUCKET_NAME = os.environ.get('BUCKETEER_BUCKET_NAME', None)

    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')

    for f in files:
        try:
            # Delete file in bucket
            obj = s3.Object(AWS_STORAGE_BUCKET_NAME, f)
            obj.delete()
        except Exception as e:
            print(e)


class ListEventosView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = EventoSerializer

    def get_queryset(self):
        # check if request.user is staff
        if self.request.user.is_staff:
            return Evento.objects.filter().order_by('fecha')
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        # check if request.user is staff
        if self.request.user.is_staff:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, pk=None):
        evento = get_object_or_404(Evento, id=pk)
        evento_serializer = EventoSerializer(evento)
        return Response({'evento': evento_serializer.data})

    def update(self, request, pk=None, **kwargs):
        evento = get_object_or_404(Evento, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            partial = kwargs.pop('partial', False)
            serializer = EventoSerializer(
                evento, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk):
        evento = get_object_or_404(Evento, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            archivos = []
            if evento.documento_excel:
                documento_excel = 'public/' + str(evento.documento_excel)
                archivos.append(documento_excel)
            if evento.logo_asamblea:
                logo_asamblea = 'public/' + str(evento.logo_asamblea)
                archivos.append(logo_asamblea)

            deleteBucketObjects(archivos)
            self.perform_destroy(evento)
            return Response({'detail': 'Evento eliminado'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)


class ListPregAbiertaView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PregAbiertaSerializer

    def get_queryset(self):
        # check if request.user is staff
        if self.request.user.is_staff:
            return PreguntaAbierta.objects.filter().order_by('enunciado')
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        # check if request.user is staff
        if self.request.user.is_staff:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, pk=None):
        pregunta = get_object_or_404(PreguntaAbierta, id=pk)
        pregunta_serializer = PregAbiertaSerializer(pregunta)
        return Response({'pregunta_abierta': pregunta_serializer.data})

    def retrieveByEvent(self, request, pk=None):
        pregunta = PreguntaAbierta.objects.filter(evento=pk)
        pregunta_serializer = PregAbiertaSerializer(pregunta, many=True)
        return Response({'pregunta_abierta': pregunta_serializer.data})

    def update(self, request, pk=None, **kwargs):
        pregunta = get_object_or_404(PreguntaAbierta, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            try:
                if request.data['activa']:
                    segundos = pregunta.timer
                    time_final = datetime.now() + timedelta(seconds=segundos)
                    time_final = time_final.time().strftime('%H:%M:%S')
                    request.data['time_final'] = time_final
            except Exception as e:
                print(e)
            partial = kwargs.pop('partial', False)
            serializer = PregAbiertaSerializer(
                pregunta, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk):
        pregunta = get_object_or_404(PreguntaAbierta, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            self.perform_destroy(pregunta)
            return Response({'detail': 'Pregunta eliminada'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)


class ListPregDecimalView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PregDecimalSerializer

    def get_queryset(self):
        # check if request.user is staff
        if self.request.user.is_staff:
            return PreguntaDecimal.objects.filter().order_by('enunciado')
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        # check if request.user is staff
        if self.request.user.is_staff:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, pk=None):
        pregunta = get_object_or_404(PreguntaDecimal, id=pk)
        pregunta_serializer = PregDecimalSerializer(pregunta)
        return Response({'pregunta_decimal': pregunta_serializer.data})

    def retrieveByEvent(self, request, pk=None):
        pregunta = PreguntaDecimal.objects.filter(evento=pk)
        pregunta_serializer = PregDecimalSerializer(pregunta, many=True)
        return Response({'pregunta_decimal': pregunta_serializer.data})

    def update(self, request, pk=None, **kwargs):
        pregunta = get_object_or_404(PreguntaDecimal, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            try:
                if request.data['activa']:
                    segundos = pregunta.timer
                    time_final = datetime.now() + timedelta(seconds=segundos)
                    time_final = time_final.time().strftime('%H:%M:%S')
                    request.data['time_final'] = time_final
            except Exception as e:
                print(e)
            partial = kwargs.pop('partial', False)
            serializer = PregDecimalSerializer(
                pregunta, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk):
        pregunta = get_object_or_404(PreguntaDecimal, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            self.perform_destroy(pregunta)
            return Response({'detail': 'Pregunta eliminada'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)


class ListPregMultipleView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PregMultipleSerializer

    def get_queryset(self):
        # check if request.user is staff
        if self.request.user.is_staff:
            return PreguntaMultiple.objects.filter().order_by('enunciado')
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def perform_create(self, serializer):
        pregunta = serializer.save()
        return pregunta

    def create(self, request, *args, **kwargs):
        # check if request.user is staff
        if self.request.user.is_staff:
            pregunta_data = request.data
            # Extrae las opciones
            opciones = pregunta_data.pop('opciones')
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            pregunta = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            for opcion in opciones:
                OpcionesMultiple.objects.create(
                    preguntaSeleccionMultiple=pregunta, **opcion
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, pk=None):
        pregunta = get_object_or_404(PreguntaMultiple, id=pk)
        pregunta_serializer = PregMultipleSerializer(pregunta)
        return Response({'pregunta_multiple': pregunta_serializer.data}, status=status.HTTP_200_OK)

    def retrieveByEvent(self, request, pk=None):
        preguntas = PreguntaMultiple.objects.filter(evento=pk)
        pregunta_serializer = PregMultipleSerializer(preguntas, many=True)
        return Response({'pregunta_multiple': pregunta_serializer.data})

    def update(self, request, pk=None, **kwargs):
        pregunta = get_object_or_404(PreguntaMultiple, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            try:
                if request.data['activa']:
                    segundos = pregunta.timer
                    time_final = datetime.now() + timedelta(seconds=segundos)
                    time_final = time_final.time().strftime('%H:%M:%S')
                    request.data['time_final'] = time_final
            except Exception as e:
                print(e)
            partial = kwargs.pop('partial', False)
            serializer = PregMultipleSerializer(
                pregunta, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk):
        pregunta = get_object_or_404(PreguntaMultiple, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            self.perform_destroy(pregunta)
            return Response({'detail': 'Pregunta eliminada'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)


class DocumentosView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = DocumentoSerializer

    def retrieveEvent(self, request, pk=None):
        documentos = Documentos.objects.filter(evento=pk).order_by('nombre')
        serializer_data = DocumentoSerializer(documentos, many=True)
        return Response({'documentos': serializer_data.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # check if request.user is staff
        if self.request.user.is_staff:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk):
        documento = get_object_or_404(Documentos, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            archivos = []
            archivos.append('public/' + str(documento.documento))
            deleteBucketObjects(archivos)
            self.perform_destroy(documento)
            return Response({'detail': 'Documento eliminado'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)


class QuorumView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = QuorumSerializer

    def retrieveByEvent(self, request, pk=None):
        # check if request.user is staff
        if self.request.user.is_staff:
            quorums = Quorum.objects.filter(evento=pk)
            serializer = QuorumSerializer(quorums, many=True)
            return Response({'quorums': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        # check if request.user is staff
        if self.request.user.is_staff:
            total_quorum = 0
            evento = get_object_or_404(Evento, id=request.data['evento'])
            asambleistas = Asambleista.objects.filter(
                evento=request.data['evento'])
            for asambleista in asambleistas:
                total_quorum += asambleista.coeficiente
            request.data['coeficiente_total'] = total_quorum
            request.data['coeficiente_registrado'] = evento.quorum
            request.data['cantidadPersonas'] = evento.cantidadQuorum
            inmuebles_registrados = InmueblesQuorum.objects.filter(
                evento=request.data['evento']).filter(registrado=False)[0]
            request.data['inmuebles_registrados'] = inmuebles_registrados.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            # Actualiza estado registrado de objeto InmueblesQuorum
            InmueblesQuorum.objects.filter(evento=request.data['evento']).filter(
                registrado=False).update(registrado=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieveEvent(self, request, pk=None):
        documentos = Documentos.objects.filter(evento=pk)
        serializer_data = DocumentoSerializer(documentos, many=True)
        return Response({'documentos': serializer_data.data}, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        quorum = get_object_or_404(Quorum, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            self.perform_destroy(quorum)
            return Response({'detail': 'Quorum eliminado'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def solicitaQuorum(request, pk=None):
    if request.user.is_staff:
        evento = get_object_or_404(Evento, id=pk)
        quorumStatus = evento.regitroQuorum
        Evento.objects.filter(id=pk).update(regitroQuorum=not(quorumStatus))
        return Response({"detail": "Se actualizó estado del quorum de la asamblea"}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def regitroQuorum(request, pk=None):
    asamb_registrados = []
    usuario = get_object_or_404(Asambleista, id=request.user.id)
    evento = get_object_or_404(Evento, id=pk)
    # Valida si existe un objeto InmueblesQuorum sin guardar
    inmuebles_registrados = InmueblesQuorum.objects.filter(
        evento=evento.id).filter(registrado=False)
    if len(inmuebles_registrados) > 0:
        # Existe un objeto previamente creado sin guardar
        asamb_registrados = inmuebles_registrados[0].inmuebles_registrados
        inmuebles_registrados = inmuebles_registrados[0]
    else:
        # Crea objeto InmueblesQuorum
        inmuebles_registrados = InmueblesQuorum.objects.create(
            evento=evento, inmuebles_registrados=asamb_registrados)
    if (usuario.quorumStatus == False) and (evento.regitroQuorum):
        quorum = evento.quorum
        quorum += usuario.coeficienteTotal + usuario.coeficiente
        cantidad = evento.cantidadQuorum + usuario.cantidadPoderes + 1
        Evento.objects.filter(id=pk).update(
            quorum=quorum, cantidadQuorum=cantidad)
        Asambleista.objects.filter(
            id=request.user.id).update(quorumStatus=True)
        # Agrega usuario al listado de asambleista presentes
        asamb_registrados.append(usuario.id)
        # Actualiza el objeto InmueblesQuorum
        InmueblesQuorum.objects.filter(pk=inmuebles_registrados.id).update(
            inmuebles_registrados=asamb_registrados)
        return Response({"detail": "El registro de asistencia del asambleista es correcto"}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "El usuario no esta habilitado para registrar quorum"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reinicioQuorum(request, pk=None):
    if request.user.is_staff:
        usuarios = Asambleista.objects.filter(
            evento=pk).update(quorumStatus=False)
        Evento.objects.filter(id=pk).update(
            regitroQuorum=False, quorum=0.0, cantidadQuorum=0)
        # Limpia lista de asambleistas registrados
        InmueblesQuorum.objects.filter(
            evento=pk).filter(registrado=False).delete()
        return Response({"detail": "Se ha reiniciado el quorum del evento"}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporteQuorum(request, pk=None):
    if request.user.is_staff:
        quorum = Quorum.objects.get(id=pk)        
        inmuebles_registrados = InmueblesQuorum.objects.get(id=quorum.inmuebles_registrados.id)
        inmuebles_presentes = []  # Lista de inmuebles presentes
        for inmueble in inmuebles_registrados.inmuebles_registrados:
            # Recorre los usuarios presentes
            try:
                usuario = Asambleista.objects.get(id=inmueble)
            except:
                return Response({"inmueble": inmueble}, status=status.HTTP_200_OK)
                
            if usuario and usuario.coeficienteTotal > 0.0:
                # El usuario tiene poderes asociados
                poderes = Apoderado.objects.filter(representado_por=usuario)
                for poder in poderes:
                    inmueble_response = dict()  # Objeto inmueble de respuesta
                    try:
                        representado = Asambleista.objects.get(id=poder.representa_a.id)
                    except:
                        representado = None
                    if representado:
                        inmueble_response['inmueble'] = representado.inmueble
                        inmueble_response['coeficiente'] = representado.coeficiente
                        inmueble_response['apoderado'] = True
                        # Agrega inmueble de representado al listado
                        inmuebles_presentes.append(inmueble_response)

            inmueble_response = dict()  # Objeto inmueble de respuesta
            inmueble_response['inmueble'] = usuario.inmueble
            inmueble_response['coeficiente'] = usuario.coeficiente
            inmueble_response['apoderado'] = False
            # Agrega inmueble de representado al listado
            inmuebles_presentes.append(inmueble_response)

        return Response(inmuebles_presentes, status=status.HTTP_200_OK)

    else:
        return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)
