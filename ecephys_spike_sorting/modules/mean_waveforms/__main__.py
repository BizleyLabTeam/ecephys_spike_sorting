from argschema import ArgSchemaParser
import os
import logging
import time

import numpy as np

from ecephys_spike_sorting.common.utils import get_ap_band_continuous_file
from ecephys_spike_sorting.common.utils import load_kilosort_data

from ecephys_spike_sorting.modules.mean_waveforms.extract_waveforms import extract_waveforms, writeDataAsNpy

def calculate_mean_waveforms(args):
    
    start = time.time()

    print("Calculating mean waveforms...")

    rawDataFile = get_ap_band_continuous_file(args['directories']['extracted_data_directory'])
    rawData = np.memmap(rawDataFile, dtype='int16', mode='r')
    data = np.reshape(rawData, (int(rawData.size/args['ephys_params']['num_channels']), args['ephys_params']['num_channels']))

    spike_times, spike_clusters, amplitudes, templates, channel_map, clusterIDs, cluster_quality = \
            load_kilosort_data(args['directories']['kilosort_output_directory'], \
                args['ephys_params']['sample_rate'], \
                convert_to_seconds = False)

    output_file = os.path.join(args['directories']['kilosort_output_directory'], 'mean_waveforms.npy')

    waveforms, spike_counts, coords, labels = extract_waveforms(data, spike_times, \
                spike_clusters, clusterIDs, \
                cluster_quality, args['ephys_params']['bit_volts'], \
                args['ephys_params']['sample_rate'], \
                args['mean_waveform_params'])

    #writeDataAsXarray(waveforms, spike_counts, coords, labels, output_file)
    writeDataAsNpy(waveforms, output_file)

    execution_time = time.time() - start
    
    return {"execution_time" : execution_time,
            "mean_waveforms_file" : output_file} # output manifest


def main():

    from ._schemas import InputParameters, OutputParameters

    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = calculate_mean_waveforms(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()