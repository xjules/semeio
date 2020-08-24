import yaml

from ert_data.measured import MeasuredData
from ert_shared.libres_facade import LibresFacade
from semeio.communication import SemeioScript

from semeio.jobs import misfit_preprocessor
from semeio.jobs.scripts.correlated_observations_scaling import (
    CorrelatedObservationsScalingJob,
)
from semeio.jobs.correlated_observations_scaling.exceptions import EmptyDatasetException
from semeio.jobs.misfit_preprocessor.exceptions import ValidationError
from semeio.jobs.misfit_preprocessor.config import (
    SPEARMAN_CORRELATION,
    AUTO_CLUSTER,
    assemble_config,
)
from semeio.jobs.spearman_correlation_job.job import spearman_job


class MisfitPreprocessorJob(SemeioScript):  # pylint: disable=too-few-public-methods
    def run_auto_cluster(
        self, misfit_preprocessor_config, measured_record, dry_run=False
    ):
        # call PCA / COS job first and get number of n_components
        config = assemble_config(misfit_preprocessor_config, measured_record)
        if not config.valid:
            raise ValidationError(
                "Invalid configuration of misfit preprocessor", config.errors
            )
        config = config.snapshot
        scaling_configs = None
        if config.clustering.method == SPEARMAN_CORRELATION:
            sconfig = config.clustering.spearman_correlation
            scaling_configs = spearman_job(
                measured_record,
                sconfig.fcluster.t,
                self._reporter,
                criterion=sconfig.fcluster.criterion,
                depth=sconfig.fcluster.depth,
                method=sconfig.linkage.method,
                metric=sconfig.linkage.metric,
            )
            scaling_params = _fetch_scaling_parameters(config_record, measured_record)
            for scaling_config in scaling_configs:
                scaling_config["CALCULATE_KEYS"].update(scaling_params)

        elif config.clustering.method == AUTO_CLUSTER:
            scaling_config = config.scaling
            try:
                nr_components = CorrelatedObservationsScalingJob(
                    self.ert()
                ).get_nr_primary_components(scaling_config)[0]
            except IndexError:
                raise AssertionError("An error when acquiring principal components!")
            except EmptyDatasetException:
                pass

            # create as many clusters (or max num clusters) as is n_components with spearmen correlation
            spearman_config = config.clustering.spearman_correlation
            scaling_configs = spearman_job(
                measured_record,
                nr_components,  # forming max nr_components clusters
                self._reporter,
                criterion="maxclust",  # this needs to be maxclust
                depth=spearman_config.fcluster.depth,
                method=spearman_config.linkage.method,
                metric=spearman_config.linkage.metric,
            )

        try:
            CorrelatedObservationsScalingJob(self.ert()).run(scaling_configs)
        except EmptyDatasetException:
            pass

    
    def run(self, *args):
        config_record = _fetch_config_record(args)
        measured_record = _load_measured_record(self.ert())
        self.run_auto_cluster(config_record, measured_record)
        # scaling_configs = misfit_preprocessor.run(
        #     **{
        #         "misfit_preprocessor_config": config_record,
        #         "measured_data": measured_record,
        #         "reporter": self.reporter,
        #     }
        # )

        # # The execution of COS should be moved into
        # # misfit_preprocessor.run when COS no longer depend on self.ert
        # # to run.
        # scaling_params = _fetch_scaling_parameters(config_record, measured_record)
        # for scaling_config in scaling_configs:
        #     scaling_config["CALCULATE_KEYS"].update(scaling_params)

        # try:
        #     CorrelatedObservationsScalingJob(self.ert()).run(scaling_configs)
        # except EmptyDatasetException:
        #     pass


def _fetch_scaling_parameters(config_record, measured_data):
    config = misfit_preprocessor.assemble_config(
        config_record,
        measured_data,
    )
    if not config.valid:
        # The config is loaded by misfit_preprocessor.run first. The
        # second time should never fail!
        raise ValueError("Misfit preprocessor config not valid on second load")

    scale_conf = config.snapshot.scaling
    return {
        "threshold": scale_conf.threshold,
    }


def _fetch_config_record(args):
    if len(args) == 0:
        return {}
    elif len(args) == 1:
        with open(args[0]) as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(
            (
                "Excepted at most one argument, namely the path to a "
                "configuration file. Received {} arguments: {}"
            ).format(len(args), args)
        )


def _load_measured_record(enkf_main):
    facade = LibresFacade(enkf_main)
    obs_keys = [
        facade.get_observation_key(nr) for nr, _ in enumerate(facade.get_observations())
    ]
    return MeasuredData(facade, obs_keys)
