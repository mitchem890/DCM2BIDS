#Use this Docker Image to build a good base for you Docker recipt you can add things to this
#To add in more functionality
docker run --rm kaczmarj/neurodocker:master generate docker \
	--base ubuntu:16.04 --pkg-manager apt \
	--dcm2niix version=latest method=source \
	--afni version=latest method=binaries \
	--fsl version=5.0.10 \
	--miniconda create_env=neuro \
		conda_install='python=3.6 numpy pandas traits' \
		pip_install='nipype pydeface' \
	--miniconda use_env=neuro \
		conda_install='jupyter' > Dockerfile


#Add in pydeface to your recipe
echo "RUN git clone https://github.com/poldracklab/pydeface.git \
&& cd pydeface \
&& python setup.py install" >> Dockerfile


#Copy over my local files into the container
echo "COPY DCM2BIDS /usr/" >> Dockerfile
echo "ENV PATH /opt/miniconda-latest/envs/neuro/bin:\$PATH" >> Dockerfile
echo "ENV HOME=/home" >> Dockerfile
echo "COPY .afnirc /home" >> Dockerfile
echo "RUN echo \"AFNI_NIFTI_TYPE_WARN = NO\" >> ~/.afnirc" >> Dockerfile
#Set it to the 
echo "ENTRYPOINT [\"python\",\"-u\",\"/usr/DCM2BIDS.py\"]" >> Dockerfile

sed -i 's/apt-get/apt-get -y/g' Dockerfile
sed -i 's/nlibxmu-headers/libxmu-headers/g' Dockerfile
sed -i 's/nmesa-common-dev/mesa-common-dev/g' Dockerfile
sed -i '/libmng1/d' Dockerfile


docker build --tag dcm2bids .
