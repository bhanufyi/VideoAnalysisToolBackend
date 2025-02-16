import scipy.signal as signal
import scipy.interpolate as interpolate
import numpy as np
from app.analysis.finderPeaksSignal import peakFinder 
 
def filter_signal(raw_signal, fs=25, cut_off_frequency=5):
    b, a = signal.butter(2, cut_off_frequency, fs=fs, btype='low', analog=False)
    return signal.filtfilt(b, a, raw_signal)
 

def get_output(up_sample_signal, duration, start_time):
    distance, velocity, peaks, indexPositiveVelocity, indexNegativeVelocity = peakFinder(up_sample_signal, fs=60,
                                                                                         minDistance=3,
                                                                                         cutOffFrequency=7.5, prct=0.05)
    line_time = []
    sizeOfDist = len(distance)
    for index, item in enumerate(distance):
        line_time.append((index / sizeOfDist) * duration + start_time)

    line_peaks = []
    line_peaks_time = []
    line_valleys_start = []
    line_valleys_start_time = []
    line_valleys_end = []
    line_valleys_end_time = []

    line_valleys = []
    line_valleys_time = []

    for index, item in enumerate(peaks):
        # ax.plot(item['openingValleyIndex'], distance[item['openingValleyIndex']], 'ro', alpha=0.75)
        # ax.plot(item['peakIndex'], distance[item['peakIndex']], 'go', alpha=0.75)
        # ax.plot(item['closingValleyIndex'], distance[item['closingValleyIndex']], 'bo', alpha=0.75)
        # line_valleys.append(prevValley+item['openingValleyIndex'])

        line_peaks.append(distance[item['peakIndex']])
        line_peaks_time.append((item['peakIndex'] / sizeOfDist) * duration + start_time)

        line_valleys_start.append(distance[item['openingValleyIndex']])
        line_valleys_start_time.append((item['openingValleyIndex'] / sizeOfDist) * duration + start_time)

        line_valleys_end.append(distance[item['closingValleyIndex']])
        line_valleys_end_time.append((item['closingValleyIndex'] / sizeOfDist) * duration + start_time)

        line_valleys.append(distance[item['openingValleyIndex']])
        line_valleys_time.append((item['openingValleyIndex'] / sizeOfDist) * duration + start_time)

    amplitude = []
    peakTime = []
    rmsVelocity = []
    speed = []
    averageOpeningSpeed = []
    averageClosingSpeed = []
    cycleDuration = []

    for idx, peak in enumerate(peaks):
        # Height measures
        x1 = peak['openingValleyIndex']
        y1 = distance[peak['openingValleyIndex']]

        x2 = peak['closingValleyIndex']
        y2 = distance[peak['closingValleyIndex']]

        x = peak['peakIndex']
        y = distance[peak['peakIndex']]

        f = interpolate.interp1d(np.array([x1, x2]), np.array([y1, y2]))

        amplitude.append(y - f(x))

        # Opening Velocity
        rmsVelocity.append(np.sqrt(np.mean(velocity[peak['openingValleyIndex']:peak['closingValleyIndex']] ** 2)))


        speed.append( (y - f(x)) / ((peak['closingValleyIndex']- peak['openingValleyIndex'])* (1 / 60)))
        averageOpeningSpeed.append((y - f(x)) / ((peak['peakIndex'] - peak['openingValleyIndex']) * (1 / 60)))
        averageClosingSpeed.append((y - f(x)) / ((peak['closingValleyIndex'] - peak['peakIndex']) * (1 / 60)))
        cycleDuration.append((peak['closingValleyIndex'] - peak['openingValleyIndex'])* (1 / 60))
        # timming
        peakTime.append(peak['peakIndex'] * (1 / 60))

    meanAmplitude = np.mean(amplitude)
    stdAmplitude = np.std(amplitude)

    meanSpeed = np.mean(speed)
    stdSpeed = np.std(speed)

    meanRMSVelocity = np.mean(rmsVelocity)
    stdRMSVelocity = np.std(rmsVelocity)
    meanAverageOpeningSpeed = np.mean(averageOpeningSpeed)
    stdAverageOpeningSpeed = np.std(averageOpeningSpeed)
    meanAverageClosingSpeed = np.mean(averageClosingSpeed)
    stdAverageClosingSpeed = np.std(averageClosingSpeed)

    meanCycleDuration = np.mean(cycleDuration)
    stdCycleDuration = np.std(cycleDuration)
    rangeCycleDuration = np.max(np.diff(peakTime)) - np.min(np.diff(peakTime))
    rate = len(peaks) / (peaks[-1]['closingValleyIndex'] - peaks[0]['openingValleyIndex']) / (1 / 60)

    earlyPeaks = peaks[:len(peaks) // 2]
    latePeaks = peaks[-len(peaks) // 2:]
    # amplitudeDecay = np.mean(distance[:len(peaks) // 3]) / np.mean(distance[-len(peaks) // 3:])
    # velocityDecay = np.sqrt(
    #     np.mean(velocity[earlyPeaks[0]['openingValleyIndex']:earlyPeaks[-1]['closingValleyIndex']] ** 2)) / np.sqrt(
    #     np.mean(velocity[latePeaks[0]['openingValleyIndex']:latePeaks[-1]['closingValleyIndex']] ** 2))
    rateDecay = (len(earlyPeaks) / ((earlyPeaks[-1]['closingValleyIndex'] - earlyPeaks[0]['openingValleyIndex']) / (1 / 60))) / (
                        len(latePeaks) / (
                        (latePeaks[-1]['closingValleyIndex'] - latePeaks[0]['openingValleyIndex']) / (1 / 60)))

    amplitudeDecay = np.array(amplitude)[:len(amplitude)//2].mean() / np.array(amplitude)[len(amplitude)//2:].mean()
    # velocityDecay = np.array(rmsVelocity)[:len(rmsVelocity)//2].mean() / np.array(rmsVelocity)[len(rmsVelocity)//2:].mean() #legacy changed to speed on 19/8/24
    velocityDecay = np.array(speed)[:len(speed)//2].mean() / np.array(speed)[len(speed)//2:].mean()


    cvAmplitude = stdAmplitude / meanAmplitude
    cvSpeed = stdSpeed / meanSpeed
    cvCycleDuration = stdCycleDuration / meanCycleDuration
    cvRMSVelocity = stdRMSVelocity / meanRMSVelocity
    cvAverageOpeningSpeed = stdAverageOpeningSpeed / meanAverageOpeningSpeed
    cvAverageClosingSpeed = stdAverageClosingSpeed / meanAverageClosingSpeed
 
    jsonFinal = {
        "linePlot": {
            "data": distance,
            "time": line_time
        },
        "velocityPlot":
        {
            "data": velocity,
            "time": line_time
        },
        "rawData":{
            "data": up_sample_signal,
            "time": line_time
        },
        "peaks": {
            "data": line_peaks,
            "time": line_peaks_time
        },
        "valleys": {
            "data": line_valleys,
            "time": line_valleys_time
        },
        "valleys_start": {
            "data": line_valleys_start,
            "time": line_valleys_start_time
        },
        "valleys_end": {
            "data": line_valleys_end,
            "time": line_valleys_end_time
        },
        "radar": {
            "A": [2.5, 3.8, 5.9, 4.2, 8.6, 4.9, 6.9, 9, 8.4, 7.3],
            "B": [3.8, 7.1, 7.4, 5.9, 4.2, 3.1, 6.5, 6.4, 3, 7],
            "labels": ["Mean Frequency", "Mean cycle amplitude", "CV cycle amplitude", "Mean cycle rms velocity",
                       "CV cycle rms velocity",
                       "Mean cycle duration", "CV cycle duration", "Range cycle duration", "Amplitude decay",
                       "Velocity decay"],
            # "velocity": velocity
        },
        "radarTable": {
            "MeanAmplitude": meanAmplitude,
            "StdAmplitude": stdAmplitude,
            "MeanSpeed": meanSpeed,
            "StdSpeed": stdSpeed,
            "MeanRMSVelocity": meanRMSVelocity,
            "StdRMSVelocity": stdRMSVelocity,
            "MeanOpeningSpeed": meanAverageOpeningSpeed,
            "stdOpeningSpeed": stdAverageOpeningSpeed,
            "meanClosingSpeed": meanAverageClosingSpeed,
            "stdClosingSpeed": stdAverageClosingSpeed,
            "meanCycleDuration": meanCycleDuration,
            "stdCycleDuration": stdCycleDuration,
            "rangeCycleDuration": rangeCycleDuration,
            "rate": rate,
            "amplitudeDecay": amplitudeDecay,
            "velocityDecay": velocityDecay,
            "rateDecay": rateDecay,
            "cvAmplitude": cvAmplitude,
            "cvCycleDuration": cvCycleDuration,
            "cvSpeed": cvSpeed,
            "cvRMSVelocity" : cvRMSVelocity,
            "cvOpeningSpeed": cvAverageOpeningSpeed,
            "cvClosingSpeed": cvAverageClosingSpeed
        },

    }

    # json_object = json.dumps(jsonFinal, default=json_serialize)
    #
    # file_name = "hand_movement_left" if is_left_leg is True else "hand_movement_right"
    # with open(file_name + ".json", "w") as outfile:
    #     outfile.write(json_object)

    return jsonFinal
