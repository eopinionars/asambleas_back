from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
import xlrd
import os
import random
import boto3
from decimal import Decimal

import smtplib
import ssl
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .models import Asambleista, Apoderado
from .serializers import AsambleistaSerializer, ApoderadosSerializer
from eventos.models import Evento
from eventos.views import deleteBucketObjects
# Create your views here.


def random_password():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()_+}{"
    password = ""
    for i in range(10):
        password += random.choice(chars)
    return password


def random_username():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()_+}{"
    username = ""
    for i in range(10):
        username += random.choice(chars)
    return username


def sendMail(body, asambleista, password, correos=None):
    try:
        email_server = smtplib.SMTP(os.environ.get(
            'EMAIL_SMTP', None), os.environ.get('EMAIL_PORT', None))
        email_server.ehlo()
        email_server.starttls()
        email_server.ehlo()
        email_server.login(os.environ.get('EMAIL_ACCOUNT', None),
                           os.environ.get('EMAIL_PASS', None))

        body_mail = """ 
        <html>\
            <body>
                <span>Reciba un cordial saludo del equipo de eOpinion | opiniones que cuentan.</span>
                <p>%s</p>                
                En esta comunicación encontrará las credenciales únicas de acceso a <span style="font-weight:bold">eOpinion-APP</span> de uso <span style="font-weight:bold">EXCLUSIVO</span> para representar la(s) unidad(es) privada(s) de acuerdo con los poderes y coeficientes corresponidentes.<br/><br/>
                Al ingresar a  <span style="font-weight:bold">eOpinion-APP</span> lencontrará la información relacionada con su participación. Por favor lea cuidadosamente el siguiente procedimiento y atienda las recomendaciones.<br/><br/>
                <ul>
                  <li>Seleccione el usuario y contraseña asignados <span style="font-weight:bold">(del primero al último caracter).</span></li>
                  <li>Cópielo con <span style="font-weight:bold">(Control C).</span></li>
                  <li>Péguelo con <span style="font-weight:bold">(Control V)</span> en el campo correspondiente en <span style="font-weight:bold">eOpinion-APP</span>, luego haga click en el botón <span style="font-weight:bold">ACCEDER.</span></li>
                  <li>Cuando haya ingresado, encontrará el enlace <span style="font-weight:bold">"Ir a la reunión"</span> el cual le dará ingreso directo a la videoconferencia.</li>
                  <li>Para asegurar su ingreso a la aplicación, evite digitar los caracteres de las credenciales, en su lugar copie y pegue.</li>
                  <li>Durante la reunión mantenga abiertas en el navegador las pestañas <span style="font-weight:bold">eOpinion-APP</span> para la votación y <span style="font-weight:bold">Zoom</span> 
                  para la videoconferencia.</li>
                  <li><span style="font-weight:bold">Recomendamos</span> ingresar desde un computador y asegúrese de haber visto el VIDEO TUTORIAL e INSTRUCTIVO suministrado por la administración.</li>
                </ul>
                <p>Para ingresar a la aplicación haga click <a href="%s"> AQUÍ</a> y utilice las siguientes credenciales.</p>       
                <span style="font-weight: bold; text-decoration: underline;">Usuario</span><span style="font-weight: bold;">: </span>%s
                <br>
                <span style="font-weight: bold; text-decoration: underline;">Contraseña</span><span style="font-weight: bold;">: </span>%s
                <br/>
                <br/>
                <span style="font-weight: bold;">Cordialmente el equipo de eOpinion</span>
            </body>
        </html>""" % (body, os.environ.get('ASAMBLEA_URL', None), asambleista.username, password)

        msg = MIMEText(body_mail, 'html')
        msg['Subject'] = 'Bienvenido a eOpinion - Estas son sus credenciales de acceso'
        msg['Disposition-Notification-To'] = os.environ.get(
            'EMAIL_ACCOUNT', None)

        # Envia correo
        if correos:
            for correo in correos.split('/'):
                email_server.sendmail(os.environ.get('EMAIL_ACCOUNT', None), str(
                    correo), msg.as_string().encode("ascii", errors="ignore"))                
        else:
            email_server.sendmail(os.environ.get('EMAIL_ACCOUNT', None), str(
                    asambleista.email), msg.as_string().encode("ascii", errors="ignore"))

        Asambleista.objects.filter(
            id=asambleista.id).update(correo_enviado=True)
        return True

    except Exception as e:
        print(e)
        return False


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def createUser(request, pk=None):
    if request.user.is_staff:
        # Lectura del archivo de Excel
        #BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        evento = Evento.objects.get(pk=pk)
        nombre_archivo = str(evento.documento_excel)
        # Valida si existe archivo para el evento
        if nombre_archivo:
            nombre_archivo = 'public/' + nombre_archivo
            # Access to S3 bucket
            AWS_ACCESS_KEY_ID = os.environ.get(
                'BUCKETEER_AWS_ACCESS_KEY_ID', '')
            AWS_SECRET_ACCESS_KEY = os.environ.get(
                'BUCKETEER_AWS_SECRET_ACCESS_KEY', '')
            AWS_STORAGE_BUCKET_NAME = os.environ.get(
                'BUCKETEER_BUCKET_NAME', '')

            s3_session = boto3.client(service_name='s3',
                                      aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            file_obj = s3_session.get_object(
                Bucket=AWS_STORAGE_BUCKET_NAME, Key=nombre_archivo)
            try:
                excel_content = file_obj['Body'].read().decode('utf-8')
            except:
                excel_content = file_obj['Body'].read().decode('windows-1252')

            excel_content = excel_content.split('\n')
            excel_content.pop(0)

            usuarios_no_creados = []
            for row in excel_content:    # Iterate through rows
                if row != '':
                    inmueble, nombres, documento, correo, celular, coeficiente, mora = row.split(
                        ',')
                    asambleista = ''
                    username = random_username()

                    if mora.lower().strip() == 'al dia':
                        mora = False
                    else:
                        mora = True

                    if inmueble != '':
                        correo_principal = correo.strip().split('/')[0]
                        asambleista = Asambleista(inmueble=inmueble.strip(), nombre_completo=nombres.strip(),
                                                  documento=documento.strip(), email=correo_principal, celular=celular.strip(), coeficiente=coeficiente.strip(),
                                                  mora=mora, username=username, evento_id=pk)
                        password = random_password()
                        asambleista.set_password(password)

                        try:
                            correosFalla = []
                            asambleista.save()
                            validaEnvio = sendMail(
                                evento.bodyCorreo, asambleista, password, correos=correo.strip())
                            if validaEnvio == False:
                                correosFalla.append(asambleista.email)

                        except:
                            usuarios_no_creados.append(inmueble)
                            pass

            if (len(usuarios_no_creados) > 0) or (len(correosFalla) > 0):
                return Response({'usuarios_no_creados': usuarios_no_creados, 'correos_fallidos': correosFalla},
                                status=status.HTTP_206_PARTIAL_CONTENT)
            else:
                return Response({'detail': 'Todos los usuarios se crearon correctamente'},
                                status=status.HTTP_201_CREATED)

        else:
            return Response({'detail': 'No existe un archivo excel asociado al evento'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)


class ListAsambleistasView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AsambleistaSerializer

    def get_queryset(self):
        # check if request.user is staff
        if self.request.user.is_staff:
            return Asambleista.objects.all()
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def perform_create(self, serializer):
        eventoBody = get_object_or_404(
            Evento, id=self.request.data['evento']).bodyCorreo
        password = self.request.data['password']
        asambleista = serializer.save()
        validaCorreo = sendMail(eventoBody, asambleista, password)
        return validaCorreo

    def create(self, request, *args, **kwargs):
        # check if request.user is staff
        if self.request.user.is_staff:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            creaUser = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            if createUser:
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({'detail': 'Error al enviar correo al usuario'}, status=status.HTTP_206_PARTIAL_CONTENT)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieveAsambleista(self, request, pk=None):
        # check if request.user is staff
        if self.request.user.is_staff:
            asambleista = get_object_or_404(Asambleista, id=pk)
            asambleista_serializer = AsambleistaSerializer(
                asambleista)
            return Response({'asambleista': asambleista_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, evento=None):
        asambleistas = Asambleista.objects.filter(evento=evento)
        asambleistas_serializer = AsambleistaSerializer(
            asambleistas, many=True)
        return Response({'asambleistas': asambleistas_serializer.data}, status=status.HTTP_200_OK)

    def update(self, request, pk=None, **kwargs):
        asambleista = get_object_or_404(Asambleista, id=pk)
        # check if request.user is staff
        # if self.request.user.is_staff:
        partial = kwargs.pop('partial', False)
        serializer = AsambleistaSerializer(
            asambleista, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
        # else:
        #    return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def resendMail(self, request, pk=None, **kwargs):
        asambleista = get_object_or_404(Asambleista, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            password = random_password()
            asambleista.set_password(password)
            asambleista.save()
            evento = get_object_or_404(Evento, id=asambleista.evento.id)
            validaCorreo = sendMail(evento.bodyCorreo, asambleista, password)
            if validaCorreo:
                serializer = AsambleistaSerializer(asambleista)
                return Response(serializer.data)
            else:
                return Response({'detail': 'No fue posible enviar el correo con las credenciales de acceso'}, status=status.HTTP_206_PARTIAL_CONTENT)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk):
        asambleista = get_object_or_404(Asambleista, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            self.perform_destroy(asambleista)
            return Response({'detail': 'Usuario eliminado'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)


class UsuarioView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AsambleistaSerializer

    def get_queryset(self):
        return Asambleista.objects.filter(id=self.request.user.id)


class ApoderadosView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ApoderadosSerializer

    def get_queryset(self):
        # if self.request.user.is_staff:
        return Apoderado.objects.all()
        # return Apoderado.objects.filter(representado_por=self.request.user.id)

    def perform_create(self, serializer):
        asambleista = get_object_or_404(Asambleista, id=self.request.user.id)
        serializer.save(representado_por=asambleista)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        apoderado = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"Apoderado creado correctamente"}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, **kwargs):
        apoderado = get_object_or_404(Apoderado, id=pk)
        representa_a = None
        try:
            representa_a = request.data['representa_a']
        except:
            pass
        # check if request.user is staff
        if self.request.user.is_staff:
            if representa_a:
                if len(Apoderado.objects.filter(representa_a=representa_a).filter(validado=True)) == 0:
                    partial = kwargs.pop('partial', False)
                    serializer = ApoderadosSerializer(
                        apoderado, data=request.data, partial=partial)
                    serializer.is_valid(raise_exception=True)
                    self.perform_update(serializer)
                    return Response(serializer.data)
                else:
                    return Response({'detail': 'El asambleista ya cuenta con otro apoderado'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                partial = kwargs.pop('partial', False)
                serializer = ApoderadosSerializer(
                    apoderado, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, pk=None):
        # check if request.user is staff
        if self.request.user.is_staff:
            apoderado = Apoderado.objects.get(id=pk)
            apoderado_serializer = ApoderadosSerializer(apoderado)
            return Response({'apoderado': apoderado_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieveByEvent(self, request, pk=None):
        # check if request.user is staff
        if self.request.user.is_staff:
            apoderados = Apoderado.objects.filter(evento=pk)
            apoderados_serializer = ApoderadosSerializer(apoderados, many=True)
            return Response({'apoderados': apoderados_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieveByAsam(self, request, pk=None):
        # check if request.user is staff
        if self.request.user.is_staff:
            apoderados = Apoderado.objects.filter(representado_por=pk)
            apoderados_serializer = ApoderadosSerializer(apoderados, many=True)
            return Response({'apoderados': apoderados_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieveByAsambleista(self, request):
        apoderado = get_object_or_404(
            Apoderado, representa_a=self.request.user.id)
        apoderado_serializer = ApoderadosSerializer(apoderado)
        return Response({'apoderado': apoderado_serializer.data}, status=status.HTTP_200_OK)

    def retrieveSelfPoderes(self, request):
        apoderados = Apoderado.objects.filter(
            representado_por=self.request.user.id)
        poderes_serializer = ApoderadosSerializer(apoderados, many=True)
        return Response({'poderes': poderes_serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        apoderado = get_object_or_404(Apoderado, id=pk)
        # check if request.user is staff
        if self.request.user.is_staff:
            archivos = []
            documento_poder = 'public/' + str(apoderado.documento_poder)
            archivos.append(documento_poder)
            deleteBucketObjects(archivos)
            self.perform_destroy(apoderado)
            return Response({'detail': 'Apoderado eliminado'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Acceso denegado. Autentiquese como usuario administrador"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def actualizaCoeficientes(request, pk=None):
    if request.user.is_staff:
        asambleista = Asambleista.objects.get(id=pk)
        apoderados_validos = Apoderado.objects.filter(
            representado_por=pk).filter(validado=True)
        total_coeficiente = asambleista.coeficienteTotal
        total_coeficiente_aldia = asambleista.coeficientePoderesDia

        if len(apoderados_validos) > 0:
            for apoderado in apoderados_validos:
                if apoderado.sumado == False:
                    total_coeficiente += apoderado.representa_a.coeficiente
                    Apoderado.objects.filter(
                        id=apoderado.id).update(sumado=True)

                    # Validacion de usuarios en mora
                    if apoderado.representa_a.mora == False:
                        total_coeficiente_aldia += apoderado.representa_a.coeficiente
                        Asambleista.objects.filter(
                            id=apoderado.representado_por.id).update(coeficientePoderesDia=total_coeficiente_aldia)

        # Desaocia el poder y resta coeficiente
        apoderados_no_validos = Apoderado.objects.filter(
            representado_por=pk).filter(validado=False).filter(sumado=True)

        if len(apoderados_no_validos) > 0:
            for apoderado in apoderados_no_validos:
                total_coeficiente -= apoderado.representa_a.coeficiente
                Apoderado.objects.filter(id=apoderado.id).update(
                    sumado=False, representa_a=None)
                # Resta coeficientes de usuarios al dia
                if apoderado.representa_a.mora == False:
                    total_coeficiente_aldia -= apoderado.representa_a.coeficiente
                    Asambleista.objects.filter(
                        id=apoderado.representado_por.id).update(coeficientePoderesDia=total_coeficiente_aldia)

        Asambleista.objects.filter(id=pk).update(
            coeficienteTotal=total_coeficiente)
        Asambleista.objects.filter(id=pk).update(
            cantidadPoderes=len(apoderados_validos))
        return Response({"coeficiente_total": total_coeficiente, "coeficiente_al_dia": total_coeficiente_aldia, "cantidadPoderes": len(apoderados_validos)})
