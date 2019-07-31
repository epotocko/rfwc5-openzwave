FROM python:3.7
RUN apt-get update && apt-get install -y udev libudev-dev

# python-openzwave dependencies
RUN pip install Cython six 'PyDispatcher>=2.0.5'

RUN mkdir /test
WORKDIR /test

# Need sendRawData function 
# https://github.com/OpenZWave/python-openzwave/pull/158
RUN git clone https://github.com/tkintscher/python-openzwave.git
WORKDIR /test/python-openzwave

# Build python-openzwave - this may take a while
RUN make build

# Create softlinks to the build in site-packages
RUN ln -s /test/python-openzwave/src-lib/libopenzwave/ /usr/local/lib/python3.7/site-packages/libopenzwave
RUN ln -s /test/python-openzwave/src-python_openzwave/python_openzwave /usr/local/lib/python3.7/site-packages/python_openzwave
RUN ln -s /test/python-openzwave/src-api/openzwave/ /usr/local/lib/python3.7/site-packages/openzwave
RUN cp /test/python-openzwave/build/lib.linux-*/libopenzwave.*.so /usr/local/lib/python3.7/site-packages/.

WORKDIR /test

COPY ./program.py /test/program.py

CMD ["python", "/test/program.py"]

